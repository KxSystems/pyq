from enchant.tokenize import Filter

class VersionFilter(Filter):
    version = ''

    def _skip(self, word):
        return word == self.version
