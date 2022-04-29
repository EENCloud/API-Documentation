


"""
Match up Eagle Eye users with rows in spreadsheet
Apply new permissions to each of them
Requires Python 3
Contact mcotton@een.com with questions
"""

import csv
import requests
from EagleEye import *

een = EagleEye()


USERNAME = ''
PASSWORD = ''
SPREADSHEET = 'file.xlsx'

een.login(username=USERNAME, password=PASSWORD)

een.get_user_list()

with open(SPREADSHEET, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        username = row[0].split(',')[0]
        email = f"{username}@something.com"

        print(f"Looking for user {email}")

        user_id = een.get_user_id_by_email(email=email)
            
        if user_id:

            person = een.get_user_details(user_id=user_id)

            if person:

                print(f"Found user {email} and their user_id is {person['id']}")

                payload = {
                            'id': person['id'],
                            'is_account_superuser': False,

                            'is_all_layout_access': False,
                            'is_edit_account': False,
                            'is_edit_admin_users': False,
                            'is_edit_all_and_add': False,
                            'is_edit_all_users': False,
                            'is_edit_camera_less_billing': False,
                            'is_edit_camera_on_off': False,
                            'is_edit_cameras': False,
                            'is_edit_map': False,
                            'is_edit_motion_areas': False,
                            'is_edit_ptz_stations': False,
                            'is_edit_sharing': False,
                            'is_edit_users': False,
                            'is_export_video': False,
                            'is_layout_admin': False,
                            'is_live_video': False,
                            'is_ptz_live': False,
                            'is_recorded_video': False,
                            'is_user_create_layout': False,
                            'is_view_all_accounts': False,
                            'is_view_preview_video': False
                        }

                # turn off admin persions
                een.update_user_details(payload)

                payload = {
                            'id': person['id'],
                            'is_account_superuser': False,
                            'is_all_layout_access': False,
                            'is_all_camera_access': True,
                            'is_edit_account': True,
                            'is_edit_admin_users': True,
                            'is_edit_all_and_add': True,
                            'is_edit_all_users': True,
                            'is_edit_camera_less_billing': True,
                            'is_edit_camera_on_off': True,
                            'is_edit_cameras': True,
                            'is_edit_map': True,
                            'is_edit_motion_areas': True,
                            'is_edit_ptz_stations': True,
                            'is_edit_sharing': True,
                            'is_edit_users': True,
                            'is_export_video': True,
                            'is_layout_admin': True,
                            'is_live_video': True,
                            'is_ptz_live': True,
                            'is_recorded_video': True,
                            'is_user_create_layout': True,
                            'is_view_all_accounts': True,
                            'is_view_preview_video': True
                        }

                een.update_user_details(payload)

            else:
                print(f"Couldn't find person: {email}")
        else:
            print(f"Couldn't find user_id: {user_id}")


