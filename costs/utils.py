def field_names(model_meta):
    """
    :param models.options.Options model_meta:
    :return:
    """
    fields = {}

    for field in model_meta.get_fields():
        try:
            fields[field.name] = model_meta.get_field(field.name).verbose_name
        except AttributeError:
            # print('%s has no verbose_name' % field.name)
            fields[field.name] = field.name

    return fields
