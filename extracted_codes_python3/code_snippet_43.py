#!/usr/bin/env python3

"""
tv: control a Sony TV

The Sony TV has a JSON REST-ish RPC interface.  We can call it.
We enter a REPL if no parameters are provided.

Beware that digits on the remote do not enter ASCII digits but some other
unicode digits.

Beware that encryption keys are not very securely managed, but I think it's
about appropriate for use as a TV remote, since I don't want to have to enter a
password to talk to the TV.  So we have a `changeme` level non-secret used as
a tiny obfuscation layer for local storage.  Since we're already storing the PIN
to talk to the TV in clear-text on disk, there's no worse vulnerability here.
"""

__author__ = 'phil@pennock-tech.com (Phil Pennock)'

import argparse
import base64
import collections
from dataclasses import dataclass
import html
import inspect
import json
import os
import pathlib
import re
import readline
import secrets
import shlex
import sys
import time
import traceback
import typing
import uuid

# TV can encrypt text strings, which we want for sending/reading passwords in app prompts
import cryptography.hazmat.backends
import cryptography.hazmat.primitives
import cryptography.hazmat.primitives.padding
# import cryptography.hazmat.primitives.asymmetric.rsa
# Sane HTTP
import requests

if sys.stdout.isatty():
    import curses
    import curses.textpad
    import io
    import pygments
    import pygments.lexers
    import pygments.formatters

if sys.version_info < (3, 6):
    raise Exception('Need at least Python 3.6 for this tool')
    # pathlib, f-strings

SCRIPT_DIR = pathlib.Path(__file__).absolute().parent

# FIXME: this is not fully XDG-compliant
_APP_NAME = pathlib.Path('tv')
_REGISTER_APP_NAME = 'tv-sony'
_HOME_DIR = _APP_NAME.home()
VERSION_INFO = '0.2.3'


def _xdg_dir(varname: str, home_rel_default: typing.Sequence[str]) -> pathlib.Path:
    ps = os.getenv(varname, None)
    if ps is None:
        p = _HOME_DIR
        for n in home_rel_default:
            p = p / n
    else:
        p = pathlib.Path(ps.split(os.path.pathsep)[0])
    return p / _APP_NAME


_CONFIG_DIR = _xdg_dir('XDG_CONFIG_HOME', ('.config',))      # read files: default.pin and default.hostname
_CACHE_DIR = _xdg_dir('XDG_CACHE_HOME', ('.cache',))         # keep a copy of the TV's public key for encryption
_DATA_DIR = _xdg_dir('XDG_DATA_HOME', ('.local', 'share',))  # keep our local private/public keys for encryption
_DEFAULT_TV = 'default'

DEF_USERAGENT = f'tv/{VERSION_INFO} (Phil Pennock)'
# This exists just for local disk and might as well be the empty string, but I
# don't want to fight APIs any more, so this is one generated password which
# I'm leaving in source, on the basis that it's like bouncycastle's "changeme"
# string: a password that's not a password, just a known serialization
# constant:
PRIVATE_KEY_PASSWORD = b'Wh#2#*4zbWBH0_o4x,Ad'


class Error(Exception):
    """Base class for exceptions from tv."""
    pass


class VolumeSpecParseError(Error):
    """Unparseable volume specification."""
    pass


class Exit(Exception):
    """Base class for exceptions which exit without a stack trace."""
    pass


class BadInput(Exit):
    """Exceptions indicating bad user input."""
    pass


class Unconfigured(Exit):
    """Missing necessary setup configuration."""
    pass


class BadAuthentication(Exit):
    """Authentication data is bad."""
    pass


# InfraRed Compatible Control data from the TV, for the SOAP interface
IRCCKeyCode = collections.namedtuple('IRCCKeyCode', ['KeyName', 'Rawcode'])

# Readline context management
# If IsCommandSet we will switch; if false, we need to figure out what to do
# differently.
# If Swallow, it takes all remaining args instead of having sub commands.
# MapSubCommands lets us build a tree.
RLContext = collections.namedtuple('RLContext', ['Name', 'IsCommandSet', 'Swallow', 'MapSubCommands'])

# curses button spec
ButtonSpec = collections.namedtuple('ButtonSpec', ['y', 'x', 'Text', 'RemoteKey'])
ButtonMade = collections.namedtuple('ButtonMade', ['top_y', 'top_x', 'height', 'width', 'pad', 'RemoteKey'])


@dataclass
class WrapCrypto:
    backend: typing.Any = cryptography.hazmat.backends.default_backend()
    DER: typing.Any = cryptography.hazmat.primitives.serialization.Encoding.DER
    PEM: typing.Any = cryptography.hazmat.primitives.serialization.Encoding.PEM
    PKCS1: typing.Any = cryptography.hazmat.primitives.serialization.PublicFormat.PKCS1
    PKCS7: typing.Any = cryptography.hazmat.primitives.padding.PKCS7
    PKCS8: typing.Any = cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8
    SPKI: typing.Any = cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
    AES: typing.Any = cryptography.hazmat.primitives.ciphers.algorithms.AES
    CBC: typing.Any = cryptography.hazmat.primitives.ciphers.modes.CBC
    PKCS1v15: typing.Any = cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15
    PrivateRaw: typing.Any = cryptography.hazmat.primitives.serialization.PrivateFormat.Raw
    Cipher: typing.Any = cryptography.hazmat.primitives.ciphers.Cipher
    # NoEncryption apparently does not satisfy KeySerializationEncryption
    # I want one fixed serialization type so I can safely load, but
    # cryptography only lets me have access to the mutable curated choice.
    BestAvailableEncryption: typing.Any = cryptography.hazmat.primitives.serialization.BestAvailableEncryption
    want_exponent: int = 65537
    want_keysize: int = 2048
    AES_BLOCKSIZE_BITS: int = 128
    AES_BLOCKSIZE_U8: int = 16


Crypto = WrapCrypto()


class SymKey:
    AES_KEY: typing.Optional[bytes] = None
    AES_IV: typing.Optional[bytes] = None

    def __init__(self):
        if SymKey.AES_KEY is None:
            SymKey.AES_KEY = secrets.token_bytes(Crypto.AES_BLOCKSIZE_U8)
        if SymKey.AES_IV is None:
            SymKey.AES_IV = secrets.token_bytes(Crypto.AES_BLOCKSIZE_U8)
        self.aes_key = SymKey.AES_KEY
        self.aes_iv = SymKey.AES_IV
        SymKey.AES_IV = (int.from_bytes(SymKey.AES_IV, byteorder='big') + 1).to_bytes(Crypto.AES_BLOCKSIZE_U8, byteorder='big')
        self.cipher = Crypto.Cipher(Crypto.AES(self.aes_key), Crypto.CBC(self.aes_iv), backend=Crypto.backend)

    def common_key(self) -> bytes:
        return self.aes_key + b':' + self.aes_iv

    def encKey(self, pubKey: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey) -> str:
        return base64.b64encode(pubKey.encrypt(
            self.common_key(),
            Crypto.PKCS1v15(),
        )).decode('ASCII')

    def encrypt(self, data: str) -> str:
        padder = Crypto.PKCS7(Crypto.AES_BLOCKSIZE_BITS).padder()
        padded = padder.update(data.encode('utf-8'))
        padded += padder.finalize()
        enc = self.cipher.encryptor()
        return base64.b64encode(enc.update(padded) + enc.finalize()).decode('ASCII')

    def decrypt(self, data: str) -> str:
        dec = self.cipher.decryptor()
        padded = dec.update(data) + dec.finalize()
        unpadder = Crypto.PKCS7(Crypto.AES_BLOCKSIZE_BITS).unpadder()
        return (unpadder.update(padded) + unpadder.finalize()).encode('utf-8')


class Config:
    """Our storage system and local RSA key mgmt."""

    PIN_OPTION, PIN_FILEEXT = 'pin', 'pin'
    HOST_OPTION, HOST_FILEEXT = 'host', 'hostname'

    def __init__(self, options: argparse.Namespace) -> None:
        self.options = options
        # .tv is the config name as given, often 'default
        # .real_tv is the actual name, use this to write files
        self.tv = self.options.tv
        self.using_default = self.tv == _DEFAULT_TV
        if self.using_default:
            self.real_tv = self._find_real_tvname()
        else:
            self.real_tv = self.tv

        try:
            self.tv_host = self.derive_field(Config.HOST_OPTION, Config.HOST_FILEEXT)
            if self.options.register:
                self.remote_name = self.options.register
            elif self.auth_cookie_file.exists():
                self.load_cookies()
            else:
                self.tv_pin = self.derive_field(Config.PIN_OPTION, Config.PIN_FILEEXT)
        except FileNotFoundError as e:
            raise Unconfigured(f'missing stored config for tv ({self.tv})') from e

        self.our_rsakey: typing.Optional[cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey] = None
        self.aes_iv: typing.Optional[bytes] = None
        self.aes_key: typing.Optional[bytes] = None
        self.max_age_app_cache = 24 * 3600

    def derive_field(self, optname: str, base: str) -> str:
        t = getattr(self.options, optname)
        if t:
            return t
        return self.read_config(base)

    def read_config(self, base: str) -> str:
        fn = _CONFIG_DIR / (self.options.tv + '.' + base)
        return fn.read_text().strip()

    def load_cookies(self) -> None:
        self.cookiejar = requests.cookies.cookiejar_from_dict(
            json.load(self.auth_cookie_file.open()),
        )

    def _find_real_tvname(self) -> str:
        # This can't use the PIN file, since that no longer necessarily exists
        default_hn_file = _CONFIG_DIR / (_DEFAULT_TV + '.' + Config.HOST_FILEEXT)
        return default_hn_file.resolve().stem

    @property
    def readline_config(self) -> pathlib.Path:
        return _CONFIG_DIR / 'readline.conf'

    @property
    def auth_cookie_file(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.cookies.json')

    @property
    def auth_uuid_file(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.uuid')

    @property
    def auth_remotename_file(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.remotename')

    @property
    def tv_keyfile(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.tv.rsa.pub')

    @property
    def tv_ircc_codes_file(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.ircc-codes.json')

    @property
    def readline_history(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.readline.history')

    @property
    def app_list_file(self) -> pathlib.Path:
        return _CACHE_DIR / (self.real_tv + '.apps.json')

    @property
    def our_public_keyfile(self) -> pathlib.Path:
        return _DATA_DIR / 'our.rsa.pub'

    @property
    def our_private_keyfile(self) -> pathlib.Path:
        return _DATA_DIR / 'our.rsa.private'

    def persist_current(self, new_tvname: str) -> None:
        # A name of '' will write out to current
        write_name = new_tvname if new_tvname else self.real_tv
        forbidden = [os.path.sep, os.path.pathsep]
        if os.path.extsep:
            forbidden += [os.path.extsep]
        if True in [c in write_name for c in forbidden]:
            raise Error(f'bad characters in {write_name!r}')

        # We will write the derived merged values, so can modify an existing TV to a new name.

        if not _CONFIG_DIR.exists():
            _CONFIG_DIR.mkdir(mode=0o700, parents=True)

        if write_name == _DEFAULT_TV:
            write_name = _DEFAULT_TV + '-real'
        pin_file = _CONFIG_DIR / (write_name + '.' + Config.PIN_FILEEXT)
        host_file = _CONFIG_DIR / (write_name + '.' + Config.HOST_FILEEXT)
        # Don't update defaults until both named entries have been written
        to_store = []
        if hasattr(self, 'tv_pin'):
            to_store.append((pin_file, self.tv_pin))
        to_store.append((host_file, self.tv_host))
        for f, content in to_store:
            if f.exists():
                f.unlink()
            f.touch(mode=0o600, exist_ok=False)
            f.write_text(content + '\n', encoding='utf-8')
        self.set_default_tv(write_name)

    def set_default_tv(self, target_tvname: str) -> None:
        # We have no locking here, so not safe against a concurrent reader.
        # For myself now, I don't currently care.
        default_pin_file = _CONFIG_DIR / (_DEFAULT_TV + '.' + Config.PIN_FILEEXT)
        default_host_file = _CONFIG_DIR / (_DEFAULT_TV + '.' + Config.HOST_FILEEXT)
        pin_file = _CONFIG_DIR / (target_tvname + '.' + Config.PIN_FILEEXT)
        host_file = _CONFIG_DIR / (target_tvname + '.' + Config.HOST_FILEEXT)
        to_link = []
        to_unlink = []
        if not host_file.exists():
            raise BadInput(f"can't repoint default TV to {target_tvname!r}, missing {host_file.name!r}")
        if not pin_file.exists():
            if not self.auth_cookie_file.exists():
                raise BadInput(f"can't repoint default TV to {target_tvname!r}, missing {pin_file.name!r}")
            else:
                to_unlink.append(default_pin_file)
        else:
            to_link.append((default_pin_file, pin_file))
        to_link.append((default_host_file, host_file))
        for src, dest in to_link:
            if src.exists() and not src.is_symlink():
                src.rename(src.with_suffix('.old' + src.suffix))
            if src.exists() or src.is_symlink():
                src.unlink()
            src.symlink_to(dest.name)
        for stale in to_unlink:
            if stale.exists():
                stale.unlink()

    def load_pubkey_b64(self, b64data: str) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey:
        return self.load_pubkey_bin(base64.b64decode(b64data, validate=True))

    def load_pubkey_bin(self, bindata: bytes) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey:
        return cryptography.hazmat.primitives.serialization.load_der_public_key(bindata, backend=Crypto.backend)

    def make_rsa_key(self) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey:
        return cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
            public_exponent=Crypto.want_exponent,
            key_size=Crypto.want_keysize,
            backend=Crypto.backend)

    def write_file(self, fpath: pathlib.Path, data: bytes) -> None:
        if not fpath.parent.exists():
            fpath.parent.mkdir(0o700)
        if fpath.exists():
            saved = fpath.with_suffix('.old' + fpath.suffix)
            if saved.exists():
                saved.unlink()
            fpath.rename(saved)
        fpath.touch(mode=0o600, exist_ok=False)
        fpath.write_bytes(data)

    def save_our_private_key(self, rsakey: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey) -> None:
        self.write_file(
            self.our_private_keyfile,
            rsakey.private_bytes(
                encoding=Crypto.PEM,
                format=Crypto.PKCS8,
                encryption_algorithm=Crypto.BestAvailableEncryption(PRIVATE_KEY_PASSWORD)),
        )

    def save_our_public_key(self, rsakey: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey) -> None:
        # We don't use this ourselves, we do this so that other tooling can look at it if wanted.
        self.write_file(
            self.our_public_keyfile,
            rsakey.public_key().public_bytes(Crypto.PEM, Crypto.PKCS1),
        )

    def setup_thisremote_encryption(self, force_new_remote_key=False) -> None:
        if self.our_private_keyfile.exists() and not force_new_remote_key:
            self.our_rsakey = cryptography.hazmat.primitives.serialization.load_pem_private_key(
                self.our_private_keyfile.read_bytes(),
                password=PRIVATE_KEY_PASSWORD,
                backend=Crypto.backend)
        else:
            self.our_rsakey = self.make_rsa_key()
            self.save_our_public_key(self.our_rsakey)
            self.save_our_private_key(self.our_rsakey)

    def load_ircc_codes(self) -> typing.Dict:
        bare = json.load(open(self.tv_ircc_codes_file))
        typed: typing.Dict[str, IRCCKeyCode] = {}
        for k, p in bare.items():
            typed[k] = IRCCKeyCode(*p)
        return typed

    def save_ircc_codes(self, jdata: typing.Dict) -> None:
        if not self.tv_ircc_codes_file.parent.exists():
            self.tv_ircc_codes_file.parent.mkdir(0o700)
        with self.tv_ircc_codes_file.open('w') as wh:
            # sort to make git and diff saner, if we move from cache
            json.dump(jdata, wh, indent=1, sort_keys=True)


class Remote:
    """Talking to the TV via various protocols.

    Most of the stuff is REST API, but anything which is directly emulating a
    remote control is IRCC-IP (InfraRed Compatible Control over Internet Protocol),
    using SOAP XML.
    """

    def __init__(self, config: Config) -> None:
        self.options = config.options
        self.config = config
        self.output = sys.stdout
        self.errstream = sys.stderr
        self.next_id = 1
        self.addr = config.tv_host
        if hasattr(config, 'tv_pin'):
            self.pin = config.tv_pin
        self._tv_pubkey_b64: typing.Optional[str] = None
        self._tv_pubkey_bin: typing.Optional[bytes] = None
        self._ircc_dict: typing.Optional[typing.Dict[str, IRCCKeyCode]] = None
        self._setup_requests()

    def verbosity(self, n: int = 1) -> bool:
        return True if self.options.verbose >= n else False

    def verbose(self, message: str, level=1) -> None:
        if self.options.verbose < level:
            return
        print('[remote] '+message, file=self.errstream, flush=True)

    def _setup_requests(self) -> None:
        self.session = requests.Session()
        self.session.headers['User-Agent'] = DEF_USERAGENT
        if hasattr(self.config, 'cookiejar'):
            self.session.cookies = self.config.cookiejar
        elif hasattr(self, 'pin'):
            self.session.headers['X-Auth-PSK'] = self.pin

    def _send(self, service: str, method: str, params: typing.Union[typing.Dict, typing.List], *, api_version='1.0'):
        url = f'http://{self.addr}/sony/{service}'
        if len(params) == 1 and '_empty' in params:
            # The introspection call, alone, seems to want [""] for params and nothing else will do.
            # (It also returns inside 'results' instead of 'result')
            payload_params = ['']
        elif params and isinstance(params, dict):
            payload_params = [params]
        elif params and isinstance(params, list):
            # remote pairing sends _two_ dictionaries
            payload_params = params
        else:
            payload_params = []
        payload_d = {
            'method': method,
            'version': api_version,
            'id': self.next_id,
            'params': payload_params
        }
        self.next_id += 1
        req = self.session.prepare_request(requests.Request('POST', url, json=payload_d))
        if self.verbosity(3):
            print(f'> POST <{url}> ', end='', file=self.output, flush=True)
            if self.verbosity(5):
                # don't use pretty_print_json, an auth header with bytes will upset the JSON encoder
                print('', file=self.output)
                for k, v in req.headers.items():
                    print(f'{k}: {v}', file=self.output)
            pretty_print_json(payload_d, stream=self.output)
        elif self.verbosity(2):
            print(f' >> {service} / {method}', file=self.output)

        # Just because I want to be able to dump all request headers, things get hairy.
        settings = self.session.merge_environment_settings(req.url, {}, None, None, None)
        r = self.session.send(req, **settings)
        return r

    def send(self, service: str, method: str, params: typing.Union[typing.Dict, typing.List], **kwargs) -> None:
        r = self._send(service, method, params, **kwargs)
        if self.verbosity():
            pretty_print_json(r.json(), stream=self.output)

    def query(self, service: str, method: str, params: typing.Union[typing.Dict, typing.List], **kwargs) -> typing.Dict:
        res = self._send(service, method, params, **kwargs)
        if self.verbosity(3):
            print(f'< {res.status_code} {res.reason}', file=self.output)
            if self.verbosity(4):
                pretty_print_json(dict(res.headers), stream=self.output)
            pretty_print_json(res.json(), stream=self.output)
        return res.json()

    def check_error(self, label: str, result: typing.Dict) -> None:
        if 'error' not in result:
            return
        code, message = result['error'][:2]
        exitmsg = f'failed in {label}: code {code} message: {message}'
        if code == 403:
            raise BadAuthentication(exitmsg)
        raise Exit(exitmsg)

    def checked_send(self, service: str, method: str, params: typing.Union[typing.Dict, typing.List], **kwargs) -> None:
        r = self._send(service, method, params, **kwargs)
        if self.verbosity():
            pretty_print_json(r.json(), stream=self.output)
        self.check_error(inspect.stack()[1].function, r.json())

    # <https://pro-bravia.sony.net/develop/integrate/rest-api/spec/>
    KNOWN_SERVICES = 'guide appControl audio avContent encryption system videoScreen'.split()

    def _get_power(self) -> str:
        resp = self.query('system', 'getPowerStatus', {})
        return resp['result'][0]['status']

    def _set_power(self, power_state: bool) -> None:
        self.checked_send('system', 'setPowerStatus', {'status': power_state})

    power = property(_get_power, _set_power, None)

    def _set_mute(self, mute_state: bool) -> None:
        self.checked_send('audio', 'setAudioMute', {'status': mute_state})

    mute = property(None, _set_mute, None)

    # this is paired with :playing, query_playing_content_info()
    # might build a map of uris to labels and try to simplify through that, for a better reader?
    def set_external_input(self, kind: str, port: str) -> None:
        uri = f'extInput:{kind}?port={port}'
        self.checked_send('avContent', 'setPlayContent', {'uri': uri})

    def _get_volume(self) -> typing.List[typing.Dict]:
        resp = self.query('audio', 'getVolumeInformation', {})
        return resp['result'][0]

    def _set_volume(self, new_volume: str) -> None:
        # api 1.2 lets us control if the on-screen volume UI should be displayed; stick to 1.0, accept UI defaults
        self.checked_send('audio', 'setAudioVolume', {'target': 'speaker', 'volume': new_volume})

    volume = property(_get_volume, _set_volume, None)

    def reboot(self) -> None:
        self.checked_send('system', 'requestReboot', {})

    def list_apps(self) -> typing.List[str]:
        apps = self.query('appControl', 'getApplicationList', {})
        self.check_error(inspect.stack()[0].function, apps)
        return [html.unescape(x['title']) for x in apps['result'][0]]

    def launch_app(self, appname: str) -> None:
        needle = appname.lower()
        res = self.query('appControl', 'getApplicationList', {})
        filtered = [app for app in res['result'][0] if html.unescape(app['title']).lower() == needle]
        if not filtered:
            raise BadInput(f'unknown app {appname!r}')
        if len(filtered) > 1:
            applist = ', '.join(map(lambda x: shlex.quote(html.unescape(x['title'])), filtered))
            raise BadInput(f'too many apps found for {appname!r}: {applist}')
        uri = filtered[0]['uri']
        self.checked_send('appControl', 'setActiveApp', {'uri': uri})

    def list_inputs(self) -> typing.List[typing.Dict]:
        inputs = self.query('avContent', 'getCurrentExternalInputsStatus', {}, api_version='1.1')
        return inputs['result'][0]

    # All methods with names starting 'query_' are directly exposed by the
    # Commander as debug commands, specified with a leading colon,
    # thus `tv :query_time` works.

    def _query_show_json(self, *args, result_index=0, **kwargs) -> None:
        res = self.query(*args, **kwargs)
        self.check_error(inspect.stack()[1].function, res)
        pretty_print_json(res['result'][result_index], stream=self.output)

    def query_supported_apis(self) -> None:
        self._query_show_json('guide', 'getSupportedApiInfo', {'services': Remote.KNOWN_SERVICES})

    def query_time(self) -> None:
        self._query_show_json('system', 'getCurrentTime', {}, api_version='1.1')

    def query_network_settings(self) -> None:
        # We shouldn't need netif per the spec, but we get "Illegal Argument" without it
        self._query_show_json('system', 'getNetworkSettings', {'netif': ''})

    def query_interface_information(self) -> None:
        self._query_show_json('system', 'getInterfaceInformation', {})

    def query_sound_settings(self) -> None:
        # Array, one for each target
        self._query_show_json('audio', 'getSoundSettings', {'target': ''}, api_version='1.1')

    def query_speaker_settings(self) -> None:
        # Array, one for each target
        self._query_show_json('audio', 'getSpeakerSettings', {'target': ''})

    def query_playing_content_info(self) -> None:
        self._query_show_json('avContent', 'getPlayingContentInfo', {})

    def setup_encryption(self, force_fetch=False, tv_only=False, **kwargs) -> None:
        if not tv_only:
            self.config.setup_thisremote_encryption(**kwargs)
        if self.config.tv_keyfile.exists() and not force_fetch:
            self._tv_pubkey_b64 = self.config.tv_keyfile.read_text().strip()
        else:
            kd = self.query('encryption', 'getPublicKey', {})
            self._tv_pubkey_b64 = kd['result'][0]['publicKey']
            if not self._tv_pubkey_b64:
                raise Exit('TV gave us an empty public key')
            if not self.config.tv_keyfile.parent.exists():
                self.config.tv_keyfile.parent.mkdir(0o700)
            self.config.tv_keyfile.write_text(self._tv_pubkey_b64 + '\n')
        self._tv_pubkey_bin = base64.b64decode(self._tv_pubkey_b64, validate=True)

    @property
    def tv_pubkey(self) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey:
        if self._tv_pubkey_bin is None:
            self.setup_encryption(tv_only=True)
            if self._tv_pubkey_bin is None:
                raise Error('still no pubkey bin after setting up encryption')
        return self.config.load_pubkey_bin(self._tv_pubkey_bin)

    def get_text_form(self) -> str:
        key = SymKey()
        encKey = key.encKey(self.tv_pubkey)
        res = self.query('appControl', 'getTextForm', {
            'encKey': encKey,
        }, api_version='1.1')
        self.check_error('get_text_form', res)
        encText = res['result'][0]['text']
        return key.decrypt(encText)

    def set_text_form(self, newText: str) -> None:
        key = SymKey()
        res = self.query('appControl', 'setTextForm', {
            'text': key.encrypt(newText),
            'encKey': key.encKey(self.tv_pubkey),
        }, api_version='1.1')
        self.check_error('set_text_form', res)
        if 'result' not in res:
            raise Error('missing result (expected empty but present) in set_text_form response')

    text = property(get_text_form, set_text_form, None)

    def _send_ircc_rawcode(self, rawcode: str) -> requests.Response:
        # <https://pro-bravia.sony.net/develop/integrate/ircc-ip/overview/index.html>
        url = f'http://{self.addr}/sony/ircc'
        soap_headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"'
        }
        soap_payload_template = '''<s:Envelope
    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">
            <IRCCCode>{0}</IRCCCode>
        </u:X_SendIRCC>
    </s:Body>
</s:Envelope>
'''
        self.verbose(f'_send_ircc_rawcode: SOAP IRCCCode {rawcode}', level=4)
        r = self.session.post(url,
                              data=soap_payload_template.format(rawcode),
                              headers=soap_headers)
        r.raise_for_status()
        return r

    def _setup_ircc(self):
        if self._ircc_dict is not None:
            return
        try:
            self._ircc_dict = self.config.load_ircc_codes()
            return
        except FileNotFoundError:
            pass
        r = self.query('system', 'getRemoteControllerInfo', {})
        self.check_error('getRemoteControllerInfo', r)
        # Ideally we'd have a handy case-insensitive dict, so we could store
        # preserving the capitalization but not worry for command entry.
        #
        # result[0] is deprecated; result[1] is list of objs, each with 'name' and 'value' keys
        codes = {}
        for pair in r['result'][1]:
            kp = pair['name']
            k = kp.lower()
            v = pair['value']
            if k in codes:
                self.verbose(f'duplicate IRCC code for {kp!r}: had: {codes[k]} also: {v}')
                continue
            codes[k] = IRCCKeyCode(kp, v)
        self.config.save_ircc_codes(codes)
        self._ircc_dict = codes

    # These _should_ be pre-empted by any actual key definitions of this name
    fallback_key_aliases = {
        'back': 'return',
        'select': 'confirm',
    }

    def key(self, keyname: str) -> None:
        self._setup_ircc()
        if self._ircc_dict is None:
            raise Error('no _ircc_dict after setup')

        # Why Num 0-9,11,12 ?  Where's the love for 10?
        if len(keyname) == 1 and keyname.isdigit() or keyname in ('Num11', 'Num12',):
            keyname = 'Num' + keyname
        lk = keyname.lower()

        if lk not in self._ircc_dict:
            if lk in self.fallback_key_aliases and self.fallback_key_aliases[lk] in self._ircc_dict:
                new_lk = self.fallback_key_aliases[lk]
                print(f'tv key: alias fixup: {lk!r} -> {new_lk!r}', file=self.errstream)
                lk = new_lk
            else:
                raise BadInput(f'unknown keycode {keyname!r}')
        self._send_ircc_rawcode(self._ircc_dict[lk].Rawcode)

    def known_keys(self) -> typing.List[str]:
        self._setup_ircc()
        if self._ircc_dict is None:
            raise Error('no _ircc_dict after setup')
        keylist = [''] * len(self._ircc_dict)
        for i, k in enumerate(self._ircc_dict.keys()):
            keylist[i] = self._ircc_dict[k].KeyName
        return sorted(keylist)

    # There's an introspection API!
    def introspect(self, service: str) -> None:
        res = self.query(service, 'getMethodTypes', {'_empty': True})
        self.check_error(inspect.stack()[0].function, res)
        pretty_print_json(res['results'], stream=self.output)

    def register_remote(self, *, nickname: str, devicename: str, pin_request_cb) -> None:
        # Found the existence of this call and the values to use in random
        # Google results, copy/pasted around the Net as samizdat.

        for drop in 'X-Auth-PSK', 'Authorization':
            if drop in self.session.headers:
                del self.session.headers[drop]

        our_uuid = str(uuid.uuid4())
        register_params = [
            {
                'clientid': nickname + ':' + our_uuid,
                'nickname': f'{nickname} ({_REGISTER_APP_NAME})',
                'level': 'private',
            },
            [
                {
                    'value': 'no',
                    'function': 'WOL',
                },
                {
                    'value': 'yes',
                    'function': 'pinRegistration',
                }
            ]
        ]

        trigger = self.query('accessControl', 'actRegister', register_params)
        # We want to raise an exception for anything _except_ a 401, which is
        # reflected in the JSON response too
        if 'error' in trigger and trigger['error'][0] == 401:
            pass
        else:
            self.check_error('register_remote', trigger)

        try:
            challenge = pin_request_cb()
        except EOFError:
            challenge = ''
        challenge = challenge.strip()
        if not challenge:
            raise Exit('no PIN entered')
        authdata = b'Basic ' + base64.b64encode(b':'+challenge.encode('latin1')).strip()

        self.next_id -= 1  # retry the _same_ request
        self.session.headers['Authorization'] = authdata.decode('ascii')
        res = self._send('accessControl', 'actRegister', register_params)
        del self.session.headers['Authorization']
        pretty_print_json(res.json(), stream=self.output)  # FIXME
        self.check_error('register_remote', res.json())

        self.config.auth_remotename_file.write_text(nickname + '\n')
        self.config.auth_uuid_file.write_text(our_uuid + '\n')
        json.dump(
            requests.utils.dict_from_cookiejar(self.session.cookies),
            self.config.auth_cookie_file.open('w'),
            indent=1, sort_keys=True)
        self.config.persist_current(devicename)

    def persist_cookies_maybe(self) -> None:
        if not hasattr(self.config, 'cookiejar'):
            return
        json.dump(
            requests.utils.dict_from_cookiejar(self.session.cookies),
            self.config.auth_cookie_file.open('w'),
            indent=1, sort_keys=True)


class SubRepl(Exception):
    """Indicate that a different REPL needs to be entered."""
    # When this is raised, the string value is used to check for a method
    # on Commander to invoke.  "cli_body_"+str(SubRepl)
    pass


class Commander:
    """Command interpreter."""

    def __init__(self, remote: Remote, commands: typing.List[str]) -> None:
        self.options = remote.options
        self.remote = remote
        self.commands = commands
        self.output = sys.stdout
        self.errstream = sys.stderr
        self.vol_matcher = re.compile(r'^([+-])(\d+)\Z')
        self.repl = False

    def _completion_init(self):
        self._completion_populate_values()
        self._complete_previous = None
        self._complete_previous_ctx = ''
        self._complete_cache_prev = None
        self._completion_context_stack = []
        self._prior_completer = None
        self._prior_push_ctx = None

    def next(self, previous: str) -> str:
        try:
            return self.commands.pop(0)
        except IndexError as e:
            raise BadInput(f'parameter needed for command {previous!r}') from e

    def volume(self, spec: str, allow_absolute: bool) -> None:
        m = self.vol_matcher.match(spec)
        if m:
            if int(m.group(2)) > 10:
                raise BadInput('can only raise/lower by up to ±10')
            self.remote.volume = spec
            return

        if not allow_absolute:
            raise VolumeSpecParseError(f'unhandled volume spec {spec!r}')
        ivol = int(spec)
        if ivol > 100:
            raise BadInput('can only set volume to absolute 0..100')
        self.remote.volume = str(ivol)

    _command_typos = {
        'hmdi': 'hdmi',
    }

    def _completion_populate_values(self) -> None:
        # FIXME: this needs to be a proper dispatch system
        all_commands = [
            'on', 'off', 'power', '?power', 'mute', 'unmute',
            'hdmi', 'composite', 'scart',
            'vol', 'volume', 'get-vol', 'get-volume', '?vol', '?volume',
            'read', 'read-text', 'write', 'write-text', 'send-text',
            'app', 'apps', '?apps', 'list-apps',
            'list-inputs', '?inputs',
            'key', ':keys',
            ':keypad',
            'danger-reboot',
            ':write', ':default', ':encrypt-setup', ':encrypt-fetch', ':about', ':playing', ':query',
            'help', '?help', ':help',  # skip '?'
            ':version',
        ] + [':'+q for q in dir(self.remote) if q.startswith('query_')]
        # If changing this from sorted, check completion logic.
        self._top_completions = sorted(all_commands)

        key_commands = self.remote.known_keys()
        self._key_completions = sorted(key_commands)

        app_cache = self.remote.config.app_list_file
        if app_cache.exists() and (time.time() - app_cache.stat().st_mtime) < self.remote.config.max_age_app_cache:
            app_names = json.load(app_cache.open())
        else:
            try:
                app_names = self.remote.list_apps()
                json.dump(app_names, app_cache.open('w'), indent=1, sort_keys=True)
            except BadAuthentication as e:
                app_names = []
                self.remote.verbose('completion setup: failed to get list of app names from the TV', level=0)
                self.remote.verbose(str(e), level=0)
        self._app_completions = sorted(app_names)

        # The MapSubCommands third item in the tuple is to let us walk down so a third level
        # could be completed by looking in that, instead of self._rl_contexts.
        self._rl_contexts = {
            'key': RLContext('key', True, True, {}),
            'app': RLContext('app', True, False, {})
        }

    def one(self, command: str) -> None:
        remote = self.remote
        if command in self._command_typos:
            print(f'tv: typo fixup: {command!r} -> {self._command_typos[command]!r}', file=self.errstream)
            command = self._command_typos[command]
        if command == 'on':
            remote.power = True
            return
        elif command == 'off':
            remote.power = False
            return
        elif command in ('power', '?power'):
            print(remote.power, file=self.output)
            return
        elif command == 'mute':
            remote.mute = True
            return
        elif command == 'unmute':
            remote.mute = False
            return
        elif command in ('hdmi', 'composite', 'scart'):
            try:
                port = str(int(self.next(command)))
            except BadInput as e:
                raise BadInput(f'command {command} needs a port (1..4)') from e
            # The actual limit might happen to be 4, but if we want to
            # _enforce_ then don't hard-code;
            # remote.send('avContent', 'getContentCount', {'source': 'extInput:hdmi'})
            # _should_ give us r['result'][0]['count']; I don't want an extra
            # RPC call for static data, so instead punt on enforcing this until
            # such time as we suck it up and build a capabilities cache in XDG
            # storage.
            remote.set_external_input(command, port)
            return
        elif command in ('vol', 'volume'):
            self.volume(self.next(command), True)
            return
        elif command in ('get-vol', 'get-volume', '?vol', '?volume'):
            pretty_print_json(remote.volume, stream=self.output)
            return
        elif command in ('read', 'read-text'):
            print(remote.text, file=self.output)
            return
        elif command in ('write', 'write-text', 'send-text'):
            remote.text = self.next(command)
            return
        elif command == 'app':
            remote.launch_app(self.next(command))
            return

        elif command in ('apps', '?apps', 'list-apps'):
            for app in sorted(remote.list_apps()):
                print(f' • {app}', file=self.output)
            return
        elif command in ('list-inputs', '?inputs'):
            maxlen_title, maxlen_label = 1, 1
            for inp in remote.list_inputs():
                tl, ll = len(inp['title']), len(inp['label'])
                if tl > maxlen_title:
                    maxlen_title = tl
                if ll > maxlen_label:
                    maxlen_label = ll
            spec = '{title:<%d}  {label:<%d}  {uri}' % (maxlen_title, maxlen_label)
            for inp in remote.list_inputs():
                print(spec.format(**inp), file=self.output)
            return

        elif command == 'key':
            try:
                keycode = self.next('keycode')
            except BadInput as e:
                if self.repl:
                    raise SubRepl(command) from e
                else:
                    raise
            #
            pause = False
            if keycode != '[':
                remote.key(keycode)
                return
            while keycode != ']':
                try:
                    keycode = self.commands.pop(0)
                    if keycode == ']':
                        break
                except IndexError:
                    return
                if pause:
                    time.sleep(0.25)
                remote.key(keycode)
                pause = True
            return
        elif command == ':keys':
            keylist = remote.known_keys()
            prev = None
            sep = ''
            for k in keylist:
                if prev is not None:
                    if k[0] != prev:
                        sep = '\n'
                    else:
                        sep = ' '
                prev = k[0]
                print(f'{sep}{k}', end='', file=self.output)
            print(file=self.output)
            return
        elif command in (':keypad', '!'):
            self.keypad_mode()
            return

        elif command == 'danger-reboot':
            remote.reboot()
            return

        # Our own house-keeping
        elif command == ':write':
            self.remote.config.persist_current(self.next(command))
            return
        elif command == ':default':
            self.remote.config.set_default_tv(self.next(command))
            return
        elif command == ':encrypt-setup':
            self.remote.setup_encryption()
            return
        elif command == ':encrypt-fetch':
            self.remote.setup_encryption(force_fetch=True)
            return

        # Keep :foo for internals and debug
        elif command == ':about':
            remote.query_interface_information()
            return
        elif command == ':playing':
            remote.query_playing_content_info()
            return
        elif command.startswith(':query_') and hasattr(remote, command[1:]):
            getattr(remote, command[1:])()
            return
        elif command == ':query':
            known = [x for x in dir(remote) if x.startswith('query_')]
            for cmd in sorted(known):
                print(':', cmd, sep='', file=self.output)
            return

        elif command in ('help', '?help', ':help', '?'):
            print('''tv: <one or more commands>
 on          off             ?power
 mute        unmute
 vol +n      vol -n          vol NN      ?vol
 hdmi N      composite N     scart N
(read-text   write-text TXT) -- BROKEN
 key KEY     key [ KEY KEY KEY ... ]
 list-inputs
 list-apps       - list installed applications
 app NAME        - launch app NAME
 danger-reboot   - reboots the TV
 :about          - basic information about the TV
 :playing        - current input source
 :query          - list various :query_* debug commands
 :write TVNAME   - write current config as TVNAME and set as default
 :default TVNAME - switch default TV to TVNAME (must exist)
 :encrypt-setup  - immediately setup encryption
 :encrypt-fetch  - force-fetch current TV public key
 :keys           - return list of known remote control keys for 'key' command
 :keypad         - enter a mode where we take arrow keys (&hjkl) to navigate
 :help, :version - the usual
If the first keycode is left-square bracket, params up until ] are all keys.
''', end='', file=self.output)
            return
        elif command == ':version':
            print(VERSION_INFO, file=self.output)
            return

        try:
            self.volume(command, False)
            return
        except VolumeSpecParseError:
            pass

        raise BadInput(f'unknown command {command!r}')

    def loop(self) -> None:
        is_subsequent = False
        while self.commands:
            if is_subsequent:
                time.sleep(0.5)
            else:
                is_subsequent = True
            self.one(self.next('').lower())

    def cli(self) -> None:
        self.repl = True
        self._completion_init()
        readline.parse_and_bind('tab: complete')
        if self.remote.config.readline_config.exists():
            readline.read_init_file(self.remote.config.readline_config)
        if hasattr(readline, 'read_history_file'):
            if self.remote.config.readline_history.exists():
                readline.read_history_file(self.remote.config.readline_history)

        print('tv: This is a TV remote control, REPL mode; :keypad or ! for keypad', file=self.output)
        print('tv: EOF (Ctrl-D) to quit, help for help, tab-completion available', file=self.output)
        print('tv: "key" to enter the remote keys mode, :keys to list known keys', file=self.output)
        print(f'tv: Target {self.remote.config.real_tv!r} [{self.remote.config.tv_host}]', file=self.output)
        self.cli_body_top()

        if hasattr(readline, 'write_history_file'):
            readline.write_history_file(self.remote.config.readline_history)

    # The completion system is a bit hairy.  It swallows exceptions, and
    # because we're in the middle of an input line we can't print there and
    # then.  So we take a two-pronged approach, with far too much logic which
    # an app shouldn't need to worry itself with (hint: a good completion
    # system would provide a diagnostic interface!):
    # 1. We import traceback and manually show exceptions ourselves, which
    #    matters with the slightly baroque calling conventions
    # 2. If verbose >= 3 then we claim the first line of the display and print
    #    diagnostic text up there.  This relies upon the common non-ANSI escape
    #    sequences to push and pop cursor position.

    def complete_debug(self, msg: str) -> None:
        if self.options.verbose < 3:
            return
        MAX = 70
        if len(msg) > MAX:
            msg = '«' + msg[-(MAX-1):]
        bookend = '\033[41;36m *** \033[m'
        buf = msg + ' ' * (MAX - len(msg))
        print(f'\033[s\033[1;1H{bookend}\033[1;35m{buf}\033[m{bookend}\033[u', end='', flush=True, file=self.output)

    def cdbg(self, append: typing.Optional[str]) -> None:
        if append is None:
            self._debug_completion_buf = ''
            return
        self._debug_completion_buf += ' ' + append
        self.complete_debug(self._debug_completion_buf)

    def push_rl_context(self, name: str) -> None:
        if hasattr(self, '_rl_context_current'):
            self._completion_context_stack.append(self._rl_context_current)
        self._rl_context_current: str = name
        self._command_set = f'_{name}_completions'

    def pop_rl_context(self) -> None:
        self._rl_context_current = self._completion_context_stack.pop()
        self._command_set = f'_{self._rl_context_current}_completions'

    def _complete_commands(self, text: str, state: int) -> typing.Optional[str]:
        # readline swallows exceptions!
        try:
            return self._complete_commands_r(text, state)
        except Exception as e:
            print(f'\noops: {e!r} inside completion', file=self.errstream)
            traceback.print_exc(file=self.output)
            raise

    def _complete_commands_r(self, text: str, state: int) -> typing.Optional[str]:
        self.cdbg(f'completion: {text!r} [{state!r}]')
        ltext = text.lower()
        if ltext and ltext[0] == "'":
            ltext = ltext[1:]
        if self._complete_previous_ctx != self._rl_context_current:
            # We have switched commands, the cache is bad.
            # Especially for the empty string case.
            self._complete_previous = None
            self._complete_cache_prev = None
            self._complete_previous_ctx = self._rl_context_current
        if self._complete_previous is not None and ltext == self._complete_previous:
            self.cdbg('match-prev')
            if self._complete_cache_prev is None:
                self.cdbg('none-avail')
                return None
            self.cdbg('cached')
            if state >= len(self._complete_cache_prev):
                self.cdbg('off-end')
                return None
            result = self._complete_cache_prev[state]
            return shlex.quote(result) if ' ' in result else result
        elif self._complete_previous is not None and ltext.startswith(self._complete_previous):
            self.cdbg('substr')
            considered = self._complete_cache_prev
        else:
            self.cdbg('reset-cand')
            considered = getattr(self, self._command_set)
        self._complete_previous, self._complete_cache_prev = None, None
        # This list is pre-sorted so that state consistently indexes it; since
        # we're caching it, that should be fine.
        avail = [c for c in considered if c.lower().startswith(ltext)]
        return_avail = [shlex.quote(c) if ' ' in c else c for c in avail]
        self._complete_previous = ltext
        if not avail:
            self.cdbg(f'none-found-({len(considered)})')
            return None
        self._complete_cache_prev = avail
        try:
            self.cdbg(f'matched-in-{len(avail)}')
            return return_avail[state]
        except IndexError:
            self.cdbg('FIN')
            return None
        self.cdbg('fell-off-end')

    def use_completer(self, name: str, push_ctx: typing.Optional[str], text: str, state: int) -> str:
        if self.options.verbose >= 4:
            print(f'use_completer {name!r} in state {state}', file=self.errstream, flush=True)
        self._prior_completer = getattr(self, name)
        self._prior_push_ctx = push_ctx
        return getattr(self, name)(text, state)

    def _rl_completer(self, text: str, state: int) -> str:
        if state != 0:
            # We're iterating to get subsequent words, re-use the same completer.
            if self._prior_completer is not None:
                if self._prior_push_ctx is None:
                    return self._prior_completer(text, state)
                else:
                    try:
                        self.push_rl_context(self._prior_push_ctx)
                        return self._prior_completer(text, state)
                    finally:
                        self.pop_rl_context()
        self._prior_completer = None

        self.cdbg(None)
        # We have text which is the current word, but we don't know the word number.
        # In theory, text == line[begin:end] after these queries:
        line = readline.get_line_buffer()
        begin = readline.get_begidx()
        end = readline.get_endidx()
        prior_words = shlex.split(line[:begin])
        self.cdbg(f'RLC {line!r} [{begin}, {end}] {prior_words!r}')
        if not prior_words:
            return self.use_completer('_complete_commands', None, text, state)
        pushed = False
        push_candidate = None
        ctx_tree = self._rl_contexts
        prior_count = len(prior_words)
        last_index = prior_count - 1
        word_index = -1
        ctx = None
        while word_index + 1 <= last_index:
            word_index += 1
            word = prior_words[word_index]
            if word in ctx_tree:
                ctx = ctx_tree[word]
                if ctx.IsCommandSet:
                    if word_index == last_index:
                        # common case
                        push_candidate = ctx.Name
                        break
                    if prior_words[word_index+1] == '[':
                        # key [ foo bar baz ] cmd2
                        # here: word_index == 0, we know there's one more
                        word_index += 1
                        ended = False
                        while word_index + 1 <= last_index:
                            word_index += 1
                            if prior_words[word_index] == ']':
                                ended = True
                                break
                        if not ended:
                            push_candidate = ctx.Name
                            break
                if not ctx.Swallow:
                    # FIXME: this is probably buggy, the type system is hinting as much.
                    ctx_tree = ctx
            # else not in ctx_tree, so it's not taking params, so stay in the current state.
        try:
            if push_candidate is not None:
                self.push_rl_context(push_candidate)
                pushed = True
                return self.use_completer('_complete_commands', push_candidate, text, state)
            else:
                return self.use_completer('_complete_commands', push_candidate, text, state)
        finally:
            if pushed:
                self.pop_rl_context()
        return None

    def cli_body_top(self):
        self.push_rl_context('top')
        readline.set_completer(self._rl_completer)
        # We mostly don't want : or ? in there because we use them as part of
        # command-names; for app names, the quote is part of the completion.
        readline.set_completer_delims(' \t\n')
        # Python default completer delims:
        #   ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'
        while True:
            try:
                if self.options.verbose >= 4:
                    print(f'ctx={self._rl_context_current!r} ' +
                          f'cmdset={self._command_set!r} ' +
                          f'stack={self._completion_context_stack!r} ' +
                          f'prev={self._complete_previous!r}',
                          file=self.errstream, flush=True)
                cmd = input('tv> ')
            except EOFError:
                print(file=self.output)
                return
            except KeyboardInterrupt as e:
                print(file=self.output)
                raise Exit(f'killed by {e!r}') from e
            try:
                cmd = cmd.strip()
                if cmd.startswith('#'):
                    continue
                self.commands = shlex.split(cmd)
                self.loop()
            except BadInput as e:
                print('tv:', e, file=self.errstream)
            except SubRepl as e:
                handler = 'cli_body_' + str(e)
                if hasattr(self, handler):
                    hold = readline.get_completer()
                    ctx_cmds = f'_{str(e)}_completions'
                    pushed = False
                    if hasattr(self, ctx_cmds):
                        self.push_rl_context(str(e))
                        pushed = True
                    getattr(self, handler)()
                    readline.set_completer(hold)
                    if pushed:
                        self.pop_rl_context()
                else:
                    raise Error(f'unknown SubRepl {e}, coding bug here') from e

    def cli_body_key(self):
        # Do we need a different history file, or prefix?
        # I think not; it hasn't happened yet, but I suspect a common pattern
        # will be to enter a key name at the top level, fail, type 'key', then
        # up-arrow twice.
        while True:
            try:
                cmd = input('tv key> ')
            except EOFError:
                print(file=self.output)
                return
            try:
                self.commands = ['key', '['] + shlex.split(cmd) + [']']
                self.loop()
            except BadInput as e:
                print('tv key:', e, file=self.errstream)

    # Rip this straight from my vlc-control project:
    # but add the return type; typing.Any for _curses.window
    def curses_pad_for_text(self, text: str, min_width=0, box=True) -> typing.Tuple[typing.Any, int, int]:
        if not text:
            return (None, 0, 0)
        lines = text.split('\n')
        if not lines[-1]:
            lines.pop()
        ysize = len(lines) + 2
        xsize = max(min_width, len(max(lines, key=len))) + 2
        pad = curses.newpad(ysize, xsize)
        if box:
            pad.box()
        for y, line in enumerate(lines):
            pad.addstr(y+1, 1, line)
        return (pad, ysize, xsize)

    def curses_reset_button_list(self):
        # typing.Any for the hidden curses _CursesWindow
        self._all_curses_buttons: typing.List[ButtonMade] = []
        # When we're looking for where a mouse-click was, we'll just walk that
        # list to see if the click was within the button; it's not efficient
        # but there's going to be "not very many" buttons, so flat-list walking
        # is tolerable.

    def curses_button(self, text: str, action: str, y: int, x: int, box=True) -> None:
        # Our assumption is that text will be Unicode with presentation
        # controls and will always look like it's one character wide.
        p = curses.newpad(3, 4)
        if box:
            p.box()
        p.addstr(1, 1, text + ' ')
        self._all_curses_buttons.append(ButtonMade(y, x, 3, 4, p, action))

    def curses_refresh_buttons(self) -> None:
        for b in self._all_curses_buttons:
            b.pad.refresh(0, 0,
                          b.top_y, b.top_x,
                          b.top_y + b.height, b.top_x+b.width)

    # nb: embedding \uFE0E to try to force text presentation doesn't seem to
    # help here, so pick symbols which don't get emojified and break our curses
    # layer.
    _ButtonList: typing.List[ButtonSpec] = [
        ButtonSpec(1, 6, '↑', 'Up'),
        ButtonSpec(1, 11, 'H', 'Home'),
        ButtonSpec(4, 1, '←', 'Left'),
        ButtonSpec(4, 6, '⏎', 'Confirm'),
        ButtonSpec(4, 11, '→', 'Right'),
        ButtonSpec(7, 1, '⮢', 'Return'),
        ButtonSpec(7, 6, '↓', 'Down'),
        ButtonSpec(10, 1, '⏸', 'Pause'),
        ButtonSpec(10, 6, '▶', 'Play'),
        ButtonSpec(10, 11, '⏹', 'Stop'),
        ButtonSpec(13, 1, '↙', 'VolumeDown'),
        ButtonSpec(13, 6, '🕪', 'Mute'),
        ButtonSpec(13, 11, '↗', 'VolumeUp'),
        # leave 16 for digits filled in separately
        ButtonSpec(19, 1, 'Y', 'Yellow'),
        ButtonSpec(19, 6, 'B', 'Blue'),
        ButtonSpec(19, 11, 'R', 'Red'),
        ButtonSpec(19, 16, 'G', 'Green'),
        ButtonSpec(19, 36, '🌍', None),
        ButtonSpec(19, 41, '🗢', 'Audio'),
        ButtonSpec(19, 46, '🖉', 'SubTitle'),
    ]

    def curses_create_buttons(self, window: typing.Any) -> None:
        self.curses_reset_button_list()
        for b in Commander._ButtonList:
            if b.RemoteKey is not None:
                self.curses_button(b.Text, b.RemoteKey, b.y, b.x)
            else:
                self.curses_button(b.Text, None, b.y, b.x, box=False)
        for d in range(10):
            ds = str(d)
            self.curses_button(ds, 'Num'+ds, 16, 1 + 5 * d)

    def curses_match_click(self, y: int, x: int) -> str:
        for b in self._all_curses_buttons:
            off_y = y - b.top_y
            off_x = x - b.top_x
            if off_y >= 0 and off_y < b.height and off_x >= 0 and off_x < b.width:
                if b.RemoteKey is None:
                    return ''
                return b.RemoteKey
        return ''

    # typing.Any for _curses.window
    def colon_mode(self, window: typing.Any, status_coords: typing.Tuple[int, int]):
        outer = curses.newwin(
            3, curses.COLS,
            status_coords[0], 0)
        outer.box()
        outer.addstr(1, 1, ': ')
        outer.refresh()
        inner = curses.newwin(1, curses.COLS - 4, status_coords[0]+1, 3)
        tb = curses.textpad.Textbox(inner)

        command_line = tb.edit()
        outer.erase()
        self.commands = shlex.split(command_line.strip())

        window.move(*status_coords)
        window.deleteln()
        window.redrawln(status_coords[0], curses.LINES - status_coords[0])
        window.refresh()

        stdout = io.StringIO()
        stderr = io.StringIO()
        cmdr_stack_out, cmdr_stack_err = self.output, self.errstream
        remote_stack_out, remote_stack_err = self.remote.output, self.remote.errstream
        self.output, self.remote.output = stdout, stdout
        self.errstream, self.remote.errstream = stderr, stderr
        # If we don't reset repl then `key` without parameters drops us back to
        # the repl out of curses _if_ we started via REPL but is rejected if
        # directly started in keypad mode.  Be consistent, temporarily wipe
        # repl.
        cmdr_repl = self.repl
        self.repl = None
        cleanups = []
        try:
            self.loop()
        except Exit as e:
            print(str(e), file=stderr)
        finally:
            emitted, cleanups = self.render_iostreams(window, status_coords, stdout, stderr)
            if emitted:
                window.timeout(-1)
                _ = window.getkey()
            while cleanups:
                window.move(cleanups.pop(-1), 0)
                window.deleteln()
            window.redrawwin()
            self.populate_screen(window)
            window.refresh()
            self.output, self.errstream = cmdr_stack_out, cmdr_stack_err
            self.remote.output, self.remote.errstream = remote_stack_out, remote_stack_err
            self.repl = cmdr_repl

    def render_iostreams(self,
                         window: typing.Any, status_coords: typing.Tuple[int, int],
                         stdout, stderr) -> typing.Tuple[bool, typing.List[int]]:
        stdout.seek(0, 0)
        stderr.seek(0, 0)
        outstr = stdout.read()
        errstr = stderr.read()
        if not (outstr or errstr):
            return False, []
        min_width = min(curses.COLS, 70)
        out_pad, out_y, out_x = self.curses_pad_for_text(outstr, min_width)
        err_pad, err_y, err_x = self.curses_pad_for_text(errstr, min_width)
        if out_y + err_y + status_coords[0] > curses.LINES:
            start_y = 1
        else:
            start_y = status_coords[0] + 1
        delete_lines_to_cleanup = []
        emitted = False
        if out_pad is not None:
            emitted = True
            show_linecount = min(out_y, curses.LINES - start_y)
            bottom = start_y + show_linecount
            out_pad.refresh(out_y - show_linecount, 0,
                            start_y, 0,
                            bottom, curses.COLS)
            if show_linecount == out_y:
                delete_lines_to_cleanup.append(start_y)
                window.move(start_y, 3)
                window.addstr('┤ stdout ├')
            start_y = bottom + 1
        if err_pad is not None and start_y < curses.LINES:
            emitted = True
            show_linecount = min(err_y, curses.LINES - start_y)
            bottom = start_y + show_linecount
            err_pad.refresh(err_y - show_linecount, 0,
                            start_y, 0,
                            bottom, curses.COLS)
            if show_linecount == err_y:
                delete_lines_to_cleanup.append(start_y)
                window.move(start_y, 3)
                window.addstr('┤ stderr ├')
            start_y = bottom + 1
        return emitted, delete_lines_to_cleanup

    def populate_screen(self, window: typing.Any) -> typing.Tuple[int, int]:
        # returns status_coords
        pad_top_y, pad_top_x = 1, 16
        pad, pad_max_y, pad_max_x = self.curses_pad_for_text('''\
  You can click on the buttons to the left, or use key-strokes.
  Arrow keys and vi hjkl to move.
  Space/Enter to confirm.
  Backspace to 'Return' (go back)
  Digits to send digit keys.  Capital 'H' for Home.
  < and > to Rewind and Forward.
  = to Pause, + to Play, - to Stop
  [ and ] to lower and increase volume, 'm' to Mute
  'a' for Audio, 's' for SubTitle
  Colors with capital initial: Yellow Blue Red Green
  : to enter colon-command mode; after output, press any key
  Esc or 'q' to quit.'''.replace('\n', ' \n'))

        self.curses_create_buttons(window)
        window.refresh()
        self.curses_refresh_buttons()
        pad.refresh(0, 0,
                    pad_top_y, pad_top_x,
                    pad_top_y+pad_max_y, pad_top_x+pad_max_x)
        window.move(pad_top_y, pad_top_x+3)
        window.addstr('┤ Keypad mode ├')
        window.move(0, 0)
        window.addstr('[ ' + self.remote.config.real_tv + ' ]')
        return (22, pad_top_x+3)

    def kp_quit(self):
        raise EOFError('Esc')

    def make_kp_actions(self, window: typing.Any, status_coords: typing.Tuple[int, int]):
        return {
            'q': self.kp_quit,
            '\033': self.kp_quit,
            'KEY_BREAK': self.kp_quit,
            'h': 'Left',
            'j': 'Down',
            'k': 'Up',
            'l': 'Right',
            'KEY_LEFT': 'Left',
            'KEY_DOWN': 'Down',
            'KEY_UP': 'Up',
            'KEY_RIGHT': 'Right',
            ' ': 'Confirm',
            'KEY_ENTER': 'Confirm',
            '\n': 'Confirm',
            '0': 'Num0',
            '1': 'Num1',
            '2': 'Num2',
            '3': 'Num3',
            '4': 'Num4',
            '5': 'Num5',
            '6': 'Num6',
            '7': 'Num7',
            '8': 'Num8',
            '9': 'Num9',
            '<': 'Rewind',
            '>': 'Forward',
            'Y': 'Yellow',
            'B': 'Blue',
            'R': 'Red',
            'G': 'Green',
            'H': 'Home',
            'KEY_BACKSPACE': 'Return',
            '\x08': 'Return',
            '\x7F': 'Return',
            '=': 'Pause',
            '+': 'Play',
            '-': 'Stop',
            '[': 'VolumeDown',
            ']': 'VolumeUp',
            'm': 'Mute',
            'a': 'Audio',
            's': 'SubTitle',
            ':': lambda: self.colon_mode(window, status_coords),
        }

    def keypad_mode(self):
        if not sys.stdout.isatty():
            raise BadInput('need stdout to be a tty for :keypad mode')

        try:
            screen = curses.initscr()

            status_coords = self.populate_screen(screen)
            screen.move(*status_coords)
            screen.deleteln()

            prior_cursor = curses.curs_set(0)
            curses.noecho()
            curses.cbreak()
            available_mouse_mask, old_mouse_mask = curses.mousemask(
                curses.BUTTON1_CLICKED | curses.BUTTON2_CLICKED | curses.BUTTON3_CLICKED,
            )
            screen.keypad(True)
            actions = self.make_kp_actions(screen, status_coords)
            screen.timeout(-1)
            while True:
                timed_out = False
                # curses.getch() documented to return -1 on timeout, but curses.getkey() is a layer around that
                # and appears to raise _curses.error on timeout.  The documentation just says "an exception".
                try:
                    c = screen.getkey()
                    if c == -1:
                        timed_out = True
                except Exception:
                    timed_out = True
                except KeyboardInterrupt as e:
                    raise Exit(f'killed by {e!r}') from e
                if timed_out:
                    screen.timeout(-1)
                    screen.move(*status_coords)
                    screen.deleteln()
                    continue
                screen.deleteln()
                screen.addstr(repr(c))
                if c == 'KEY_MOUSE':
                    try:
                        m_id, m_x, m_y, m_z, m_bstate = curses.getmouse()
                        screen.addstr(f' ({m_bstate})')
                        found = self.curses_match_click(m_y, m_x)
                        if found and m_bstate & curses.BUTTON1_CLICKED:
                            self.remote.key(found)
                            screen.addstr(f' [{found}]')
                        elif found:
                            screen.addstr(' (ignoring non-button1)')
                        else:
                            screen.addstr(' <no-button>')
                    except Exception:
                        screen.addstr(' BOGUS')
                elif c in actions:
                    if callable(actions[c]):
                        actions[c]()
                    else:
                        screen.addstr(' → ' + str(actions[c]))
                        self.remote.key(actions[c])
                else:
                    curses.beep()
                screen.move(*status_coords)
                screen.timeout(3 * 1000)  # milliseconds
        except EOFError:
            pass
        finally:
            screen.keypad(False)
            curses.mousemask(old_mouse_mask)
            curses.nocbreak()
            curses.echo()
            curses.curs_set(prior_cursor)
            curses.endwin()


if sys.stdout.isatty():
    _pp_lexer = pygments.lexers.JsonLexer()
    _pp_formatter = pygments.formatters.TerminalFormatter()

    def pretty_print_json(data, stream=None) -> None:
        if stream is None:
            stream = sys.stdout
        laid_out = json.dumps(data, sort_keys=True, indent=2)
        print(pygments.highlight(laid_out, _pp_lexer, _pp_formatter), file=stream)
else:
    def pretty_print_json(data, stream=None) -> None:
        if stream is None:
            stream = sys.stdout
        print(json.dumps(data, sort_keys=True, indent=2), file=stream)


def _setup_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-t', '--tv',
                        type=str, default=_DEFAULT_TV,
                        help='Override configuration name for TV [%(default)s]')
    parser.add_argument('-H', '--host',
                        type=str, default='',
                        help='Override TV host/IP [%(default)s]')
    parser.add_argument('--pin',
                        type=str, default='',
                        help='override PIN from config')
    parser.add_argument('--register',
                        type=str, default='',
                        help='Name of this remote to register with the TV (instead of PIN)')
    parser.add_argument('--reregister', '--re-register',
                        action='store_true', default=False,
                        help='Force re-register of current TV')
    parser.add_argument('-v', '--verbose',
                        action='count', default=0,
                        help='Be more verbose')
    parser.add_argument('--version',
                        action='store_true', default=False,
                        help='Show version and exit')
    parser.add_argument('rest', nargs='*', metavar='Command',
                        help='TV commands to issue (try :help)')
    return parser


def _main(args: typing.List[str], argv0: str) -> int:
    parser = _setup_cli_parser()
    options = parser.parse_args(args=args)

    if options.version:
        print(VERSION_INFO)
        return 0

    try:
        config = Config(options)
    except Unconfigured as e:
        print('tv: no configuration stored?', file=sys.stderr)
        print('tv: setup with: tv --host <HOST> --pin <SECRET> :write your-tv-name-here', file=sys.stderr)
        raise e

    remote = Remote(config)

    if options.register or options.reregister:
        if options.reregister and not options.register:
            options.register = config.real_tv

        def challenge_pin_entry():
            # I don't think there's any point using getpass, since anything
            # being entered here is visible to everyone who can see the TV, so
            # probably more than can see the computer screen.  So make it easy
            # to see both and compare, by leaving echo on.
            return input('PIN on screen> ')
        remote.register_remote(
            nickname=options.register,
            devicename=config.real_tv,
            pin_request_cb=challenge_pin_entry)
        return 0

    commander = Commander(remote, options.rest)
    try:
        if options.rest:
            commander.loop()
        else:
            commander.cli()
    finally:
        remote.persist_cookies_maybe()

    return 0


if __name__ == '__main__':
    argv0 = pathlib.Path(sys.argv[0]).name
    if argv0.endswith('.py'):
        argv0 = argv0[:-3]
    tracer = None

    def _start(): return _main(sys.argv[1:], argv0=argv0)
    start = _start
    rv = 0
    if os.environ.get('TRACE_' + argv0.upper(), None):
        ignore = [sys.prefix, sys.exec_prefix]
        if 'PYENV_ROOT' in os.environ:
            ignore.append(os.environ['PYENV_ROOT'])
        import trace
        tracer = trace.Trace(
            ignoredirs=ignore,
            count=0,  # skip .cover generation
        )

        def start(): return tracer.run('_start()')
    try:
        rv = start()
    except Exit as e:
        for arg in e.args:
            print('{}: {}'.format(argv0, arg), file=sys.stderr)
        sys.exit(1)
    finally:
        if tracer:
            tracer.results().write_results()
    sys.exit(rv)

# Debugging:
# import pathlib; __name__, __file__ = 'debug-tv', 'tv'; exec(pathlib.Path('tv').read_text())
if __name__ == 'debug-tv':
    parser = _setup_cli_parser()
    options = parser.parse_args(args=[':help'])
    if 'VERBOSE' in os.environ:
        options.verbose = int(os.environ['VERBOSE'])
    config = Config(options)
    remote = Remote(config)

# vim: set ft=python sw=4 expandtab :
