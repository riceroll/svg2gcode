def translate(points, vec):
    """
    :param points: [point_0, point_1, ...]
         point: {'x', 'y', 'layer_thickness', 'E_ratio'}
    :param vec: [trans_x, trans_y]
    :return: points: [point_0, point_1, ...]
        point: {'x': translated, 'y': translated, 'layer_thickness', 'E_ratio'}
    """
    for i, point in enumerate(points):
        points[i]['x'] += vec[0]
        points[i]['y'] += vec[1]
    return points


def scale(points, factor):
    """
    :param points: [point_0, point_1, ...]
         point: {'x', 'y', 'layer_thickness', 'E_ratio'}
    :param factor: float, scaling factor
    :return: points: [point_0, point_1, ...]
        point: {'x': translated, 'y': translated, 'layer_thickness', 'E_ratio'}
    """
    for i, point in enumerate(points):
        points[i]['x'] *= factor
        points[i]['y'] *= factor
    return points

