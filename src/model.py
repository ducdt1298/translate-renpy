class Info:
    def __init__(self, path, original_language, into_language):
        self.path = path
        self.original_language = original_language
        self.into_language = into_language


class FileObject:
    def __init__(self, id, path, status):
        self.id = id
        self.path = path
        self.status = status


class DialogueObject:
    def __init__(self, id, ord, text, status, file_id):
        self.id = id
        self.ord = ord
        self.text = text
        self.status = status
        self.file_id = file_id


class PhraseObject:
    def __init__(self, id, ord, text, space_before, space_after, need_translate, status, dialogue_id):
        self.id = id
        self.ord = ord
        self.text = text
        self.space_before = space_before
        self.space_after = space_after
        self.need_translate = need_translate
        self.status = status
        self.dialogue_id = dialogue_id


class SpaceObject:
    def __init__(self, space_before, space_after):
        self.space_before = space_before
        self.space_after = space_after
