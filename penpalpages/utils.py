LANGUAGE_CHOICES = (
    ("1", "English"),
    ("2", "Hindi"),
    ("3", "Sanskrit"),
    ("4", "Tamil"),
    ("5", "Telugu"),
)


def from_label_to_values(request, field):
    if field == 'speaks':
        labels = request.user.profile.speaks
    else:
        labels = request.user.profile.is_learning

    # we have selected labels user profile and converting it into values
    if labels is not None:
        values = [value for value, label in LANGUAGE_CHOICES if label in labels]
        # get the value of those labels from LANGUAGE_CHOICES if they are present in labels from above
        # but those values are in string ['1','2']
        values = [int(i) for i in values]
    else:
        values = ''
        # if user is new profile then above else condition
    return values


# elements is the list received result is output and other two param is to differentiate which is what
def sort(elements, results, lang_speaks=False, lang_learning=False):
    if len(elements)> 1:
        for e in range(len(elements)):
            # we don't need to filter for 0 as we already did this in view.
            if e == 0:
                continue
            if lang_speaks:
                results = results.filter(speaks__icontains=elements[e])
            if lang_learning:
                results = results.filter(is_learning__icontains=elements[e])
    return results
