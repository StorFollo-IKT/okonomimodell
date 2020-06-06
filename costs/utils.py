def field_names(model_meta):
    """
    :param models.options.Options model_meta:
    :return:
    """
    fields = {}

    for field in model_meta.get_fields():
        fields[field.name] = model_meta.get_field(field.name).verbose_name

    return fields
