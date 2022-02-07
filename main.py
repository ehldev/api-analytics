from flask import Flask, jsonify
import json
from flask_cors import CORS

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
CORS(app)

@app.route('/')
def inicio():
    return 'Python and Google Analytics API 1.0.0'

# Devolverá información general
@app.route('/company_view_id/<view_id>')
def init_app(view_id):
    # Por año
    page_views_year = get_data(view_id, 'ga:pageviews')
    page_views_year = page_views_year["reports"][0]["data"]["rows"][0]["metrics"][0]["values"][0]

    # Última mes
    page_views_last_month = get_data(view_id, 'ga:pageviews', '30daysAgo', 'today')
    page_views_last_month = page_views_last_month["reports"][0]["data"]["rows"][0]["metrics"][0]["values"][0]
    
    # Última semana
    page_views_last_week = get_data(view_id, 'ga:pageviews', '7daysAgo', 'today')
    page_views_last_week = page_views_last_week["reports"][0]["data"]["rows"][0]["metrics"][0]["values"][0]

    # Hoy
    # page_views_today = get_data(view_id, 'ga:pageviews', '1daysAgo', 'today')
    # page_views_today = page_views_today["reports"][0]["data"]["rows"][0]["metrics"][0]["values"][0]

    # Último mes con país de usuarios
    users_per_countries = get_users_per_countries(view_id, 'ga:pageviews', '30daysAgo', 'today')
    users_per_countries = users_per_countries["reports"][0]["data"]["rows"]

    # Último mes con ciudad de usuarios
    users_per_city = get_users_per_city(view_id, 'ga:pageviews', '30daysAgo', 'today')
    users_per_city = users_per_city["reports"][0]["data"]["rows"]

    # Browser
    users_browsers = get_user_browser(view_id, '30daysAgo', 'today')
    users_browsers = users_browsers["reports"][0]["data"]["rows"]

    # Sistema operativo
    users_systems = get_user_system(view_id, '30daysAgo', 'today')
    users_systems = users_systems["reports"][0]["data"]["rows"]

    # Primera página visitada por los usuarios
    first_page = get_landing_page(view_id, '30daysAgo', 'today')
    first_page = first_page["reports"][0]["data"]["rows"]

    # Categoría de dispositivos
    category_devices = get_category_devices(view_id)
    category_devices = category_devices["reports"][0]["data"]["rows"]

    return jsonify({
        "view_id": view_id,
        "page_views_year": page_views_year,
        "page_views_last_week": page_views_last_week,
        # "page_views_today": page_views_today,
        "page_views_last_month": page_views_last_month,
        "users_per_countries": users_per_countries,
        "users_per_city": users_per_city,
        "users_browsers": users_browsers,
        "users_systems": users_systems,
        "first_page": first_page,
        "category_devices": category_devices
    })


# Lógica para obtener datos de Google Analytics
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './client_secrets.json'
# 259696991

# Inicializar consulta de reportes
def initialize_analyticsreporting():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics

def get_data(view_id, metric, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    options = {
        'viewId': view_id,
        'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
        'metrics': [{'expression': metric}]
    }

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                options
            ]
        }
    ).execute()

def get_users_per_countries(view_id, metric, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    options = {
        'viewId': view_id,
        'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
        'metrics': [{'expression': metric}],
        'dimensions': [{'name': 'ga:country'}]
    }

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                options
            ]
        }
    ).execute()

def get_users_per_city(view_id, metric, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    options = {
        'viewId': view_id,
        'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
        'metrics': [{'expression': metric}],
        'dimensions': [{'name': 'ga:country'}]
    }

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                options
            ]
        }
    ).execute()

def get_users_per_city(view_id, metric, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    options = {
        'viewId': view_id,
        'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
        'metrics': [{'expression': metric}],
        'dimensions': [{'name': 'ga:city'}]
    }

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                options
            ]
        }
    ).execute()


#view_id, startDate='7daysAgo', endDate='today'
def get_page_views(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'metrics': [{'expression': 'ga:pageviews'}],
                    # 'dimensions': [{'name': 'ga:country'}]
                }]
        }
    ).execute()

def get_user_browser(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:browser'}]
                }]
        }
    ).execute()

def get_user_system(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:operatingSystem'}]
                }]
        }
    ).execute()

# Última página visitada antes de salir
def get_user_last_page(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:exitPagePath'}]
                }]
        }
    ).execute()

# Primera página visitada por los usuarios
def get_landing_page(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:landingPagePath'}],
                    'metrics': [{'expression': "ga:entrances"}]
                }]
        }
    ).execute()

# Usuarios activos en los últimos 30 días
def get_category_devices(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:deviceCategory'}],
                    # 'metrics': [{'expression': "ga:entrances"}]
                }]
        }
    ).execute()

def get_user_gender(view_id, startDate='2022-01-01', endDate='today'):
    analytics = initialize_analyticsreporting()

    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
                    'dimensions': [{'name': 'ga:userGender'}]
                }]
        }
    ).execute()

app.run(debug=True)