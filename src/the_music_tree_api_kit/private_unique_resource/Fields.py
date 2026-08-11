from the_music_tree_api_kit.private.Fields import Fields as PrivateFields
from the_music_tree_api_kit.public_standard_resource.Fields import Fields as PublicRelationFields
from the_music_tree_api_kit.uuid.Fields import Fields as UuidFields


class Fields(PublicRelationFields, PrivateFields, UuidFields):
    pass
