# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json, urllib

class Synonyms(kp.Plugin):
    """
    One-line description of your plugin.

    This block is a longer and more detailed description of your plugin that may
    span on several lines, albeit not being required by the application.

    You may have several plugins defined in this module. It can be useful to
    logically separate the features of your package. All your plugin classes
    will be instantiated by Keypirinha as long as they are derived directly or
    indirectly from :py:class:`keypirinha.Plugin` (aliased ``kp.Plugin`` here).

    In case you want to have a base class for your plugins, you must prefix its
    name with an underscore (``_``) to indicate Keypirinha it is not meant to be
    instantiated directly.

    In rare cases, you may need an even more powerful way of telling Keypirinha
    what classes to instantiate: the ``__keypirinha_plugins__`` global variable
    may be declared in this module. It can be either an iterable of class
    objects derived from :py:class:`keypirinha.Plugin`; or, even more dynamic,
    it can be a callable that returns an iterable of class objects. Check out
    the ``StressTest`` example from the SDK for an example.

    Up to 100 plugins are supported per module.

    More detailed documentation at: http://keypirinha.com/api/plugin.html
    """

    API_URL='https://api.api-ninjas.com/v1/thesaurus?word={}'
    API_KEY = ''
    # API_KEY='R7VTVKcgcGsroBBSP3WF6w==PJ6LIT57QJUbts6r'
    IDLE_TIME = 0.25
    DICT_ITEMCAT = kp.ItemCategory.USER_BASE + 1
    ANSWER_ITEMCAT = kp.ItemCategory.USER_BASE + 2
    COPY_ITEMCAT = kp.ItemCategory.USER_BASE + 2

    def __init__(self):
        super().__init__()

    def _make_request(self, query):
        url = self.API_URL.format(query)
        opener = kpnet.build_urllib_opener()
        opener.addheaders = [("X-Api-Key", self.API_KEY)]
        with opener.open(url) as conn:
            return conn.read()

    def _parse_response(self, response):
        results = []
        js = json.loads(response)
        for word in js['synonyms']:
            results.append(word)
        return(results)

    def _thesaurus_search(self, query):
        response_list = self._parse_response(self._make_request(query))
        return response_list

    def on_start(self):
        settings = self.load_settings()

        self.API_KEY = settings.get_stripped("API_KEY", section = "main")

        self.set_actions(self.COPY_ITEMCAT, [
            self.create_action(
                name="copy",
                label="Copy",
                short_desc="Copy the definition"
                )])

    def on_catalog(self):
        self.set_catalog([self.create_item(
            category=self.DICT_ITEMCAT,
            label="Synonyms",
            short_desc="Find synonyms of a word",
            target="Synonyms",
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.NOARGS
        )])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[-1].category() != self.DICT_ITEMCAT:
            return

        if self.should_terminate(self.IDLE_TIME):
            return
        
        _user_input = user_input.strip()

        result = None
        synonyms = []

        if _user_input == "":
            return

        try:
            result = self._thesaurus_search(_user_input.lower())
        except urllib.error.HTTPError as ex:
            self.info(ex)
            if len(_user_input) > 1:
                synonyms.append(self.create_error_item(
                label=user_input,
                short_desc="Word not found: " + _user_input,
            ))
        except Exception as ex:
            synonyms.append(self.create_error_item(
                label=user_input,
                short_desc="Error: " + str(ex),
            ))

        if result:
            for word in result:
                synonyms.append(self.create_item(
                    category=self.ANSWER_ITEMCAT,
                    label=word,
                    short_desc="Press Enter to copy the result",
                    target=word,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE
                ))

        self.set_suggestions(synonyms, kp.Match.ANY, kp.Sort.NONE)



    def on_execute(self, item, action):
        kpu.set_clipboard(item.target())

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass
