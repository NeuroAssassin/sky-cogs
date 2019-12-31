import ast
import textwrap
import inspect

# For possible errors encountered via ast
import discord
from discord.ext import commands
import custom_classes as cc
import aiohttp
import asyncio
import json


class Ast:
    def __init__(self, coro):
        self.ifs = []
        self.errors = []
        self.code = ast.parse(textwrap.dedent(inspect.getsource(coro)))

        self.orelse(self.code.body[0].body[1])
        self.generate_errors()

    def generate_errors(self):
        for i in self.ifs:
            func = getattr(i.test, "func")
            if func and self.bir(func).get("id", "") == "isinstance":
                value = i.test.args[1]
                value_d = self.bir(value)
                if value_d.get("id"):
                    self.errors.append(eval(value.id))
                elif value_d.get("value"):
                    self.errors.append(eval(self.do_at(value.value, value.attr)))
                elif value_d.get("elts"):
                    for error in value.elts:
                        if self.bir(error).get("id"):
                            self.errors.append(eval(error.id))
                        elif self.bir(error).get("value"):
                            self.errors.append(eval(self.do_at(error.value, error.attr)))

    def orelse(self, node):
        if isinstance(node, ast.If):
            self.ifs.append(node)
        node = getattr(node, "orelse", [])
        if node and isinstance(node[0], ast.If):
            self.orelse(node[0])

    def bir(self, obj):
        return {i: getattr(obj, i) for i in dir(obj) if not i.startswith("__") and "_" not in i}

    def do_at(self, node, name):
        if isinstance(node, ast.Name):
            return f"{node.id}.{name}"
        if isinstance(node.value, ast.Attribute):
            return self.do_at(node.value, f"{node.attr}.{name}")
        else:
            return f"{node.value.id}.{node.attr}.{name}"
