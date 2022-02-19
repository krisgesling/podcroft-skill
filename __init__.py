from mycroft import MycroftSkill, intent_file_handler


class Podcroft(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('podcroft.intent')
    def handle_podcroft(self, message):
        podcast_name = message.data.get('podcast_name')

        self.speak_dialog('podcroft', data={
            'podcast_name': podcast_name
        })


def create_skill():
    return Podcroft()

