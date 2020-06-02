from django import template

register = template.Library()


@register.filter(name='addcss') # фильтр добавляет css классы и id. Классы в шаблоне должны идти друг за другом, и разделяться пробелом, id должно начинаться на # и стоять в самом конце. Пример: {{ field|addcss:"my_first_class my_second_class my_n_class #my_id"}}
def addclass(value, arg):
    css_classes = value.field.widget.attrs.get('class', '').split(' ')
    if arg.split(' ')[-1].startswith('#'):
        css_id = arg.split(' ')[-1][1:]
        arg = arg.split(' ')[:-1]
    else:
        css_id = ''
        arg = arg.split(' ')
    if css_classes and sorted(arg) != sorted(css_classes):
        css_classes = '{} {}'.format(' '.join(arg),' '.join(css_classes))

    return value.as_widget(attrs={'class': css_classes, 'id': css_id})
