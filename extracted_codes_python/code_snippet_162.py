# coding: utf-8

"""
    Gate API v4

    Welcome to Gate.io API  APIv4 provides spot, margin and futures trading operations. There are public APIs to retrieve the real-time market statistics, and private APIs which needs authentication to trade on user's behalf.  # noqa: E501

    Contact: support@mail.gate.io
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from gate_api.configuration import Configuration


class FlashSwapCurrency(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'currency': 'str',
        'min_amount': 'str',
        'max_amount': 'str',
        'swappable': 'list[str]'
    }

    attribute_map = {
        'currency': 'currency',
        'min_amount': 'min_amount',
        'max_amount': 'max_amount',
        'swappable': 'swappable'
    }

    def __init__(self, currency=None, min_amount=None, max_amount=None, swappable=None, local_vars_configuration=None):  # noqa: E501
        # type: (str, str, str, list[str], Configuration) -> None
        """FlashSwapCurrency - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._currency = None
        self._min_amount = None
        self._max_amount = None
        self._swappable = None
        self.discriminator = None

        if currency is not None:
            self.currency = currency
        if min_amount is not None:
            self.min_amount = min_amount
        if max_amount is not None:
            self.max_amount = max_amount
        if swappable is not None:
            self.swappable = swappable

    @property
    def currency(self):
        """Gets the currency of this FlashSwapCurrency.  # noqa: E501

        Currency name  # noqa: E501

        :return: The currency of this FlashSwapCurrency.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this FlashSwapCurrency.

        Currency name  # noqa: E501

        :param currency: The currency of this FlashSwapCurrency.  # noqa: E501
        :type: str
        """

        self._currency = currency

    @property
    def min_amount(self):
        """Gets the min_amount of this FlashSwapCurrency.  # noqa: E501

        Minimum amount required in flash swap  # noqa: E501

        :return: The min_amount of this FlashSwapCurrency.  # noqa: E501
        :rtype: str
        """
        return self._min_amount

    @min_amount.setter
    def min_amount(self, min_amount):
        """Sets the min_amount of this FlashSwapCurrency.

        Minimum amount required in flash swap  # noqa: E501

        :param min_amount: The min_amount of this FlashSwapCurrency.  # noqa: E501
        :type: str
        """

        self._min_amount = min_amount

    @property
    def max_amount(self):
        """Gets the max_amount of this FlashSwapCurrency.  # noqa: E501

        Maximum amount allowed in flash swap  # noqa: E501

        :return: The max_amount of this FlashSwapCurrency.  # noqa: E501
        :rtype: str
        """
        return self._max_amount

    @max_amount.setter
    def max_amount(self, max_amount):
        """Sets the max_amount of this FlashSwapCurrency.

        Maximum amount allowed in flash swap  # noqa: E501

        :param max_amount: The max_amount of this FlashSwapCurrency.  # noqa: E501
        :type: str
        """

        self._max_amount = max_amount

    @property
    def swappable(self):
        """Gets the swappable of this FlashSwapCurrency.  # noqa: E501

        Currencies which can be swapped to from this currency  # noqa: E501

        :return: The swappable of this FlashSwapCurrency.  # noqa: E501
        :rtype: list[str]
        """
        return self._swappable

    @swappable.setter
    def swappable(self, swappable):
        """Sets the swappable of this FlashSwapCurrency.

        Currencies which can be swapped to from this currency  # noqa: E501

        :param swappable: The swappable of this FlashSwapCurrency.  # noqa: E501
        :type: list[str]
        """

        self._swappable = swappable

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FlashSwapCurrency):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FlashSwapCurrency):
            return True

        return self.to_dict() != other.to_dict()
