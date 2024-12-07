#!/usr/bin/env python3
'''Script to generate a Backstage catalog-config.yaml file from a meta.yaml file.'''

import os
import argparse
import glob
import yaml
from mergedeep import merge, Strategy
from github import Github


class CreateBackstageConfig():
    '''Class that does all of the things to generate Backstage catalog-config.yaml'''

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Metadata to Backstage config conversion tool.')
        self.parser.add_argument(
            '-g', '--glob', action='store_true',
            help='Glob entire repo for meta.yaml files.', required=False)
        self.args = self.parser.parse_args()

    def run(self):
        '''Process args and kick things off'''

        #Glob for meta files and process them individually
        if self.args.glob:
            meta_path = ""
            catalog_path = ""
            catalog_yaml = {}
            files = glob.glob('./**/*meta.yaml',
                          recursive = True)

            for filename in files:
                catalog_docs = []
                catalog_component = {}
                data = {}
                meta_path = filename
                catalog_path = meta_path.removesuffix('meta.yaml')
                catalog_path += 'catalog-info.yaml'
                data = self.get_local_meta_yaml(meta_path)

                if os.path.exists(catalog_path):
                    catalog_yaml = self.get_local_catalog_yaml(catalog_path)
                    catalog_component, catalog_docs = self.parse_catalog_yaml(catalog_yaml)

                self.process_meta(catalog_path, catalog_component, catalog_docs, data)


        #Use root dir meta.yaml file + parse root catalog-info.yaml
        else:
            catalog_yaml = {}
            catalog_component = {}
            catalog_docs = []
            data = {}
            print("No repo specified. Using local meta.yaml.")
            data = self.get_local_meta_yaml('./meta.yaml')

            if os.path.exists('./catalog-info.yaml'):
                catalog_yaml = self.get_local_catalog_yaml('./catalog-info.yaml')
                catalog_component, catalog_docs = self.parse_catalog_yaml(catalog_yaml)

            self.process_meta("./catalog_info.yaml",  catalog_component, catalog_docs, data)

    def process_meta(self, catalog_path, catalog_component, catalog_docs, data):
        '''Process meta yaml data into final catalog file'''

        component = {}
        depends = {}
        merged_components = {}
        final_yaml = []

        if data:
            component = self.generate_component(data["meta_yaml"])
            if data["meta_yaml"]["ndustrial"]["depends"]:
                depends = self.generate_depends(data["meta_yaml"]["ndustrial"]["depends"])
                component["spec"]["dependsOn"] = depends

        #Merge catalog-info.yaml with meta.yaml
        if catalog_component:
            merged_components = self.merge_components(catalog_component, component)

        #Merge component and any additional yaml docs
        if catalog_docs:
            final_yaml.append(merged_components)
            for i in catalog_docs:
                final_yaml.append(i)
        else: 
            final_yaml = [component]

        with open(catalog_path, 'w') as file:
            yaml.dump_all(final_yaml, file)


    def get_remote_meta_yaml(self, repo):
        '''UNUSED Build meta yaml dir'''
        yml = {}
        # Get file and return conents
        res = self.github_get_file(repo, "/", "meta.yaml")

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def get_local_meta_yaml(self, meta_path):
        '''Function to get a local meta.yaml file'''
        yml = {}

        res = open(meta_path, 'r')

        if res:
            yml = self.parse_meta_yaml(res)

        return {"meta_yaml": yml}

    def parse_meta_yaml(self, meta):
        '''Function to parse a local meta yaml contents into yaml object'''
        keys = ["name", "organization", "owner",
                "managed_by", "project", "type", "depends"]

        yml = yaml.safe_load(meta)

        #Loop through keys to and set to none if does not exist
        for i in yml:
            if i == "ndustrial":
                for j in keys:
                    if yml["ndustrial"].get(j) is None:
                        yml["ndustrial"][j] = None

        return yml

    def parse_catalog_yaml(self, catalog):
        '''Function to break apart component and other docs from a pre-existing catalog-info.yaml'''
        docs_list = []
        component = {}
        for i in yaml.safe_load_all(catalog):
            if i["kind"] == "Component":
                component = i
            else:
                docs_list.append(i)
        return component, docs_list

    def get_local_catalog_yaml(self,catalog_path):
        '''Function to read a local catalog-info.yaml'''

        res = open(catalog_path, 'r')

        return res

    def generate_component(self, meta):
        '''Create a Backstage component object based on meta.yml contents'''

        component = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": meta["ndustrial"]["name"],
                "annotations": {
                    "github.com/project-slug": meta["ndustrial"]["project"]
                }
            },
            "spec": {
                "type": meta["ndustrial"]["type"],
                "system": meta["ndustrial"]["project"],
                "lifecycle": "production",
                "owner": meta["ndustrial"]["owner"]

            }
        }
        return component

    def generate_depends(self, meta_depends):
        '''Create depends array from the depend field in meta.yml'''
        depends_on_list = []
        for dependency in meta_depends:
            if "project" in dependency:
                env = dependency.get("env", "default")
                depends_on_list.append(f"component:{env}/{dependency['name']}")
            if "external" in dependency:
                env = dependency.get("env", "default")
                depends_on_list.append(f"resource:{env}/{dependency['name']}")
        return depends_on_list

    def merge_components(self, catalog, meta):
        '''Run deepmerge to capture diffs from catalog-info and meta'''

        res = merge({}, meta, catalog, strategy=Strategy.ADDITIVE)
        return res

    def github_get_file(self, repo, path, f_name):
        '''(UNUSED) Check repo for file and return contents of file'''

        github_connection = self.github_auth()

        try:
            res = github_connection.get_repo(repo)
        except Exception as github_error:
            print(f"Unable to get repo: {repo}\nError: {github_error}")
            return None

        #Check if f_name file exists in root dir of repo
        if f_name in [i.path for i in res.get_contents(path)]:
            file_content = res.get_contents(f_name)
            return file_content.decoded_content.decode()

        print(f"{f_name} not found in path of {path}")

        return None

    def github_auth(self):
        '''(UNUSED) Authenticate to github using local GITHUB_TOKEN env'''
        if os.getenv('GITHUB_TOKEN') is None:
            print("GITHUB_TOKEN env variable not set. Please set and re-run script.")
            return None

        token = os.getenv('GITHUB_TOKEN')
        return Github(token)

if __name__ == '__main__':
    CreateBackstageConfig().run()
