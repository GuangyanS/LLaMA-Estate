import difflib
import json
import re
import string
import seaborn as sns
import pandas as pd
from geopy.distance import geodesic
from matplotlib import pyplot as plt
from unidecode import unidecode
import argparse

city_distance_df = pd.read_csv('data/city_name_duplication_analysis.csv', encoding='utf-8')

def clean_text(text):
    if text is None:
        return ''
    # Ensure text is a string
    text = str(text)
    # Remove accents
    text = unidecode(text)
    # Remove all punctuations and spaces
    text = re.sub(r'[' + string.punctuation + ']', '', text).lower()
    return text

def similarity_score(feature, advert_data, feedback_data) -> float:
    advert_value = advert_data.get(feature)
    feedback_value = feedback_data.get(feature)

    cleaned_str1 = clean_text(advert_value)
    cleaned_str2 = clean_text(feedback_value)

    if len(cleaned_str1) < 1 or len(cleaned_str2) < 1:
        return 0.0

    str1_words = set(cleaned_str1.split())
    str2_words = set(cleaned_str2.split())

    intersection = len(str1_words.intersection(str2_words))
    union = len(str1_words.union(str2_words))

    return intersection / union if union != 0 else 0.0

def compare_title(advert_data, feedback_data):
    threshold = 0.7
    if similarity_score("title", advert_data, feedback_data) >= threshold:
        return 1.0
    return round(similarity_score("title", advert_data, feedback_data), 1)

def compare_summary(advert_data, feedback_data):
    threshold = 0.7
    if similarity_score("summary", advert_data, feedback_data) >= threshold:
        return 1.0
    return round(similarity_score("summary", advert_data, feedback_data), 1)

def compare_price(advert_data, feedback_data, allowed_difference=1):
    """allow difference"""
    advert_price = advert_data.get("price")
    feedback_price = feedback_data.get("price")

    if advert_price in [None, ''] or feedback_price in [None, '']:
        return False

    try:
        advert_price = int(advert_price)
        feedback_price = int(feedback_price)
    except ValueError:
        return False

    return abs(advert_price - feedback_price) <= allowed_difference

def compare_h_surface(advert_data, feedback_data, allowed_difference=100):
    advert_surface = advert_data.get("h_surface")
    feedback_surface = feedback_data.get("h_surface")

    # Check for special string cases
    if isinstance(advert_surface, str) and isinstance(feedback_surface, str):
        if advert_surface.lower() == feedback_surface.lower():
            return True

    # Try to convert to integers and compare
    try:
        advert_surface = int(advert_surface)
        feedback_surface = int(feedback_surface)
        return abs(advert_surface - feedback_surface) <= allowed_difference
    except (ValueError, TypeError):
        # One or both values are not numbers, comparison cannot be made
        return False

def compare_l_surface(advert_data, feedback_data, allowed_difference=100):
    advert_surface = advert_data.get("l_surface")
    feedback_surface = feedback_data.get("l_surface")

    # Check for special string cases
    if isinstance(advert_surface, str) and isinstance(feedback_surface, str):
        if advert_surface.lower() == feedback_surface.lower():
            return True

    # Try to convert to integers and compare
    try:
        advert_surface = int(advert_surface)
        feedback_surface = int(feedback_surface)
        return abs(advert_surface - feedback_surface) <= allowed_difference
    except (ValueError, TypeError):
        # One or both values are not numbers, comparison cannot be made
        return False

def compare_room(advert_data, feedback_data):
    return is_equal("n_rooms", advert_data, feedback_data)

def compare_bed(advert_data, feedback_data):
    return is_equal("n_beds", advert_data, feedback_data)

def compare_pic(advert_data, feedback_data):
    return is_equal("n_pics", advert_data, feedback_data)

def _is_zero_value(value):
    value = str(value).lower()
    return value in ('0', '', 'none', 'null')

def is_equal(feature, advert_data, feedback_data):
    advert_value = advert_data.get(feature)
    feedback_value = feedback_data.get(feature)

    if advert_value is None or feedback_value is None:
        return False

    return _is_zero_value(advert_value) and _is_zero_value(feedback_value) or str(advert_value).lower() == str(feedback_value).lower()

def compare_type(advert_data, feedback_data):
    return is_equal("type", advert_data, feedback_data)


def compare_description(advert_data, feedback_data):
    return is_equal("description", advert_data, feedback_data)

def compare_postal(advert_data, feedback_data):
    return is_equal("postal_code", advert_data, feedback_data)

def compare_lat(advert_data, feedback_data):
    return is_equal("latitude", advert_data, feedback_data)

def compare_lng(advert_data, feedback_data):
    return is_equal("longitude", advert_data, feedback_data)

# def compare_location(advert_data, feedback_data):
#     """
#     Compares the distance between two locations given their latitude and longitude.
#     Returns True if they are within 10 kilometers of each other, else False.
#     Considers 'not found' as a valid value if it matches in both coordinates.
#
#     :param advert_data: Dictionary containing the latitude and longitude of the first location.
#     :param feedback_data: Dictionary containing the latitude and longitude of the second location.
#     :return: Boolean indicating whether the two locations are within 10 kilometers of each other.
#     """
#     advert_value_lat = advert_data.get('latitude')
#     advert_value_lng = advert_data.get('longitude')
#     feedback_value_lat = feedback_data.get('latitude')
#     feedback_value_lng = feedback_data.get('longitude')
#     advert_city = advert_data.get('city')
#     feedback_city = feedback_data.get('city')
#
#     # Check if coordinates match exactly (including 'not found')
#     if (advert_value_lat, advert_value_lng) == (feedback_value_lat, feedback_value_lng):
#         return True
#
#     try:
#         # If coordinates do not match exactly, calculate distance
#         coords_1 = (float(advert_value_lat), float(advert_value_lng))
#         coords_2 = (float(feedback_value_lat), float(feedback_value_lng))
#
#         city_row = city_distance_df[city_distance_df['city'] == advert_city]
#         # If the city is duplicated and the min_distance is not 0
#         if not city_row.empty and city_row['min_distance'].iloc[0]:
#             min_distance = city_row['min_distance'].iloc[0]
#             if geodesic(coords_1, coords_2).kilometers <= min_distance:
#                 return True
#         else:
#             return compare_postal(advert_data, feedback_data)
#     except (ValueError, TypeError):
#         # In case of any error in conversion or calculation, assume mismatch
#         return False


def compare_location(advert_data, feedback_data):
    """
    Compares the distance between two locations given their latitude and longitude.
    Returns True if they are within 10 kilometers of each other, else False.
    Considers 'not found' as a valid value if it matches in both coordinates.

    :param advert_data: Dictionary containing the latitude and longitude of the first location.
    :param feedback_data: Dictionary containing the latitude and longitude of the second location.
    :return: Boolean indicating whether the two locations are within 10 kilometers of each other.
    """
    advert_value_lat = advert_data.get('latitude')
    advert_value_lng = advert_data.get('longitude')
    feedback_value_lat = feedback_data.get('latitude')
    feedback_value_lng = feedback_data.get('longitude')
    advert_city = advert_data.get('city')
    feedback_city = feedback_data.get('city')

    # Check if coordinates match exactly (including 'not found')
    if (advert_value_lat, advert_value_lng) == (feedback_value_lat, feedback_value_lng):
        return True

    try:
        # If coordinates do not match exactly, calculate distance
        coords_1 = (float(advert_value_lat), float(advert_value_lng))
        coords_2 = (float(feedback_value_lat), float(feedback_value_lng))

        # if advert_city in city_distance_df['city'].values:
        #     min_distance = city_distance_df[city_distance_df['city'] == advert_city]['min_distance'].iloc[0]
        #     if 0 < min_distance < 100:
        #         return geodesic(coords_1, coords_2).kilometers <= 10
        #     if min_distance > 100:
        #         return geodesic(coords_1, coords_2).kilometers <= 50
        if geodesic(coords_1, coords_2).kilometers <= 10:
            return True

        else:
            return compare_postal(advert_data, feedback_data)
    except (ValueError, TypeError):
        # In case of any error in conversion or calculation, assume mismatch
        return False

def compare_city(advert_data, feedback_data):
    return is_equal("city", advert_data, feedback_data)

def evaluate_advert(advert_data, feedback_data):
    evaluation_results = {
        "price": compare_price(advert_data, feedback_data),
        "city": compare_city(advert_data, feedback_data),
        "postal_code": compare_postal(advert_data, feedback_data),
        # "latitude": compare_lat(advert_data, feedback_data),
        # "longitude": compare_lng(advert_data, feedback_data),
        "location": compare_location(advert_data, feedback_data),
        "description": compare_description(advert_data, feedback_data),
        "title": compare_title(advert_data, feedback_data),
        "summary": compare_summary(advert_data, feedback_data),
        "type": compare_type(advert_data, feedback_data),
        "h_surface": compare_h_surface(advert_data, feedback_data),
        "l_surface": compare_l_surface(advert_data, feedback_data),
        "n_rooms": compare_room(advert_data, feedback_data),
        "n_beds": compare_bed(advert_data, feedback_data),
        # "n_pics": compare_pic(advert_data, feedback_data),
    }
    return evaluation_results

def main(data_folder):
    # 读取标签和预测数据
    with open(f'{data_folder}/label_data.json', 'r', encoding='utf-8') as f:
        label_data = json.load(f)

    with open(f'{data_folder}/predict_data.json', 'r', encoding='utf-8') as f:
        predict_data = json.load(f)

    # 评估所有广告
    all_evaluation_results = {}
    for index in label_data.keys():
        all_evaluation_results[index] = evaluate_advert(label_data[index], predict_data[index])

    # 转换为DataFrame
    evaluation_df = pd.DataFrame.from_dict(all_evaluation_results, orient='index')

    # 计算每个特征匹配成功的百分比
    percentage_true = evaluation_df.mean() * 100
    percentage_true_df = percentage_true.reset_index()
    percentage_true_df.columns = ['Feature', 'Percentage of True']
    print(percentage_true_df)

    # 绘制特征匹配统计图
    feature_match_count = evaluation_df.sum().sort_values()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=feature_match_count.values, y=feature_match_count.index)
    plt.xlabel('Number of Matches')
    plt.ylabel('Features')
    plt.title('Feature Match Count')
    plt.show()

    # 绘制每条广告的匹配分布图
    ads_match_count = evaluation_df.sum(axis=1)
    plt.figure(figsize=(10, 6))
    sns.histplot(ads_match_count, bins=30, kde=True)
    plt.xlabel('Number of Feature Matches')
    plt.ylabel('Number of Ads')
    plt.title('Distribution of Feature Matches per Ad')
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate label and prediction data.')
    parser.add_argument('--data_folder', type=str, required=True, help='Folder path containing data files')
    args = parser.parse_args()
    main(args.data_folder)
