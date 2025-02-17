
from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost

import logging
import re
import os
import shutil
import yaml

from . import mux, webpilot

backend_mapping = {
    "webpilot": webpilot.process,
    "native": mux.process,
}

process: callable = None
config: dict = None

# Register plugin
@register(name="WebVisite", description="基于GPT的函数调用能力，为QChatGPT提供网页访问功能", version="0.1.1", author="s2cr3t")
class WebVisite(Plugin):

    # Triggered when plugin is loaded
    def __init__(self, plugin_host: PluginHost):
        global process, config
        # Check if webwlkr.yaml exists
        if not os.path.exists("webwlkr.yaml"):
            shutil.copyfile("plugins/WebVisitePlugin/config-template.yaml", "webwlkr.yaml")
        
        # Read configuration file
        with open("webwlkr.yaml", "r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        process = backend_mapping[config["backend"]]

    @func("visite_the_web")
    def _(url: str, brief_len: int = 4090):
        """Call this function to viste website when asking you to visite some web.but DO NOT use this function to search things
        - Summary the plain content result by yourself

        Args:
            url(str): url to visite
            brief_len(int): max length of the plain text content, recommend 1024-4096, prefer 4096. If not provided, default value from config will be used.

        Returns:
            str: plain text content of the web page or error message(starts with 'error:')
        """
        try:
           
                return process(url, brief_len)
        except Exception as e:
            logging.error("[Webwlkr] error visit web: {}".format(e))
            return "error visit web:{}".format(e)

    # Triggered when plugin is uninstalled
    def __del__(self):
        pass

def process_search_results(search_results: list, brief_len: int):
    """Process search results and return text content"""
    brief_text = ""
    for result in search_results:
        title = result['title']
        abstract = result['abstract']
        url = result['url']
        # 将标题和摘要添加到brief_text中
        brief_text += f"Title: {title}\nSnippet: {abstract}\nurl:{url}\n\n "
    

    return brief_text.strip() if brief_text else "No relevant results found."
