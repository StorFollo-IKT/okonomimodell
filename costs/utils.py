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


def filter_list(field, model=None, queryset=None):
    """
    Generate a list with field values to be used with filter lists
    :param field: Field name
    :param model: Model object
    :param queryset: Queryset object
    :return: list with values
    """
    if model:
        queryset = model.objects.all()
    return list(queryset.values_list(field, flat=True))
