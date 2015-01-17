from django.conf import settings
from django.db import models
from django.db import connection
from django.utils.importlib import import_module

from Crypto.Cipher import AES
from Crypto import Random


class EncryptedField(Exception):
    pass


class AESField(models.TextField):

    description = 'A field that uses AES encryption.'
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.aes_prefix = kwargs.pop('aes_prefix', 'aes:')
        if not self.aes_prefix:
            raise ValueError('AES Prefix cannot be null.')
        self.aes_method = getattr(settings, 'AES_METHOD', 'dailienator.common.aesfield.default')
        self.aes_key = kwargs.pop('aes_key', '')
        super(AESField, self).__init__(*args, **kwargs)

    def get_aes_key(self):
        result = import_module(self.aes_method).lookup(self.aes_key)
        if len(result) < 10:
            raise ValueError('Passphrase cannot be less than 10 chars.')
        return result

    def get_prep_lookup(self, type, value):
        raise EncryptedField('You cannot do lookups on an encrypted field.')

    def get_db_prep_lookup(self, *args, **kw):
        raise EncryptedField('You cannot do lookups on an encrypted field.')

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared and value:
            return self.aes_prefix + self._encrypt(value)
        return value

    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    unpad = lambda s : s[:-ord(s[len(s)-1:])]

    def _encrypt( self, value ):
        value = pad(value)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.get_aes_key(), AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( value ) )

    def to_python(self, value):
        if not value or not value.startswith(self.aes_prefix):
            return value
        return self._decrypt(value[len(self.aes_prefix):])

    def _decrypt( self, value ):
        value = base64.b64decode(value)
        iv = value[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( value[16:] ))


# South support.
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(rules=[(
        (AESField,),
        [],
        {
            'aes_prefix': ['aes_prefix', {'default': 'aes:'}],
            'aes_key': ['aes_key', {'default': ''}],
        },
    )], patterns=['^dailienator\.common\.aesfield\.field\.AESField'])
