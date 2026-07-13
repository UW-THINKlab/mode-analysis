def update_confusion_matrix_new_threshold(confusion_matrix,
                                          prediction,
                                          actual_mode):
    if prediction == "walk":
        col = 0
    elif prediction == "bike":
        col = 1
    elif prediction == "taxi":
        col = 2
    elif prediction == "bus":
        col = 3
    elif prediction == "subway":
        col = 4
    elif prediction == "train":
        col = 5
    elif prediction == "airplane":
        col = 6
    else:
        col = -1

    if actual_mode == "walk" or actual_mode == "run":
        row = 0
    elif actual_mode == "bike":
        row = 1
    elif actual_mode == "taxi" or actual_mode == "car":
        row = 2
    elif actual_mode == "bus":
        row = 3
    elif actual_mode == "subway":
        row = 4
    elif actual_mode == "train":
        row = 5
    elif actual_mode == "airplane":
        row = 6
    else:
        row = -1

    confusion_matrix[row, col] = confusion_matrix[row, col] + 1

def update_confusion_matrix_rmove(confusion_matrix,
                                  prediction,
                                  actual_mode):
    if prediction == "walk":
        col = 0
    elif prediction == "bike":
        col = 1
    elif prediction == "car":
        col = 2
    elif prediction == "transit":
        col = 3
    elif prediction == "other":
        col = 4
    else:
        col = -1

    if actual_mode == "walk":
        row = 0
    elif actual_mode == "bike":
        row = 1
    elif actual_mode == "car":
        row = 2
    elif actual_mode == "transit":
        row = 3
    elif actual_mode == "other":
        row = 4
    else:
        row = -1

    confusion_matrix[row, col] = confusion_matrix[row, col] + 1