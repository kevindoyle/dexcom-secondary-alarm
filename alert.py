

def decide_alert(bg_list, threshold=55):
    return all(bg < threshold for bg in bg_list)