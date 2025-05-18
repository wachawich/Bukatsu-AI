from flask import request, jsonify
from collections import Counter
from db.db_connection import get_db_connection

from logic.user import get_user
from logic.activityType import getActivityTypeInteresting, getActivityType
from logic.favorite import getFavActivityType
from model.callModel import predict_lgbm

def processFunction(model):
    data = request.get_json()

    fields = [
        "all", "user_sys_id"
    ]
    
    print(data['user_sys_id'])
    print(data['all'])

    if not any(data.get(field) for field in fields):
        return jsonify({"success": False, "message": "No value input!"}), 400

    user_id = data['user_sys_id']
    
    activityTypeInList = []
    activityTypeList = []
    favActivityTypeList = []
    
    if user_id > 0 :
        activityTypeUserInteresting = getActivityTypeInteresting(user_id)
        activityType = getActivityType()
        favActivityType = getFavActivityType(user_id)
        
        for ActyInter in activityTypeUserInteresting:
            activityTypeInList.append(ActyInter['activity_type_name_th'])
        
        for ActypeData in activityType:
            activityTypeList.append(ActypeData['activity_type_name_th'])
            
        for FavActypeData in favActivityType:
            favActivityTypeList.append(FavActypeData['activity_type_name_th'])
    
        
        processJson = process_user_by_id(user_id, activityTypeInList, favActivityTypeList, activityTypeList)
        print("processJson", processJson)
        
        prediction_data = predict_lgbm(processJson, model)
        
        return jsonify({"success": True, "data": processJson, "predict" : prediction_data}), 200
    elif data['all'] > 0 :
         return jsonify({"success": True, "data": "sima"}), 400
    else :
        return jsonify({"success": True, "data": "rows"}), 400


def examplePrediction(model):
    data = request.get_json()

    fields = [
        "all", "user_sys_id"
    ]
    
    print(data['user_sys_id'])
    print(data['all'])

    if not any(data.get(field) for field in fields):
        return jsonify({"success": False, "message": "No value input!"}), 400

    user_id = data['user_sys_id']
    
    activityTypeInList = []
    activityTypeList = []
    favActivityTypeList = []
    
    if user_id > 0 :
        activityTypeUserInteresting = getActivityTypeInteresting(user_id)
        activityType = getActivityType()
        favActivityType = getFavActivityType(user_id)
        
        for ActyInter in activityTypeUserInteresting:
            activityTypeInList.append(ActyInter['activity_type_name_th'])
        
        for ActypeData in activityType:
            activityTypeList.append(ActypeData['activity_type_name_th'])
            
        for FavActypeData in favActivityType:
            favActivityTypeList.append(FavActypeData['activity_type_name_th'])
    
        
        processJson = process_user_by_id(user_id, activityTypeInList, favActivityTypeList, activityTypeList)
        print("processJson", processJson)
        
        prediction_data = predict_lgbm(processJson, model)
        
        return jsonify({"success": True, "data": processJson, "predict" : prediction_data}), 200
    elif data['all'] > 0 :
         return jsonify({"success": True, "data": "sima"}), 400
    else :
        return jsonify({"success": True, "data": "rows"}), 400


def process_user_by_id(user_sys_id, user_interesting_activity_type, user_fav_activity_type, activity_type):
    user = get_user(user_sys_id)
    
    print(user)
    
    interesting = {
            activity: 1 if activity in user_interesting_activity_type else 0
            for activity in activity_type
    }
    
    counts = Counter(user_fav_activity_type)
    full_counts = {activity: counts.get(activity, 0) for activity in activity_type}
    
    click = []
    countsClick = Counter(click)
    fullcountsClick = {activity: countsClick.get(activity, 0) for activity in activity_type}
    
    user_info = {}
    
    user_info['gender'] = user[0]['sex']
    user_info['role'] = user[0]['role_name']
    user_info['interesting'] = interesting
    user_info['favorite'] = full_counts
    user_info['click'] = fullcountsClick
    
    return user_info