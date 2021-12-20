import contextlib
#from collections import namedtuple
from datetime import datetime, timedelta, date

import mysql.connector

from shared.configProd import config_conn


def call_proc_results(cursor, stored_procedure_name, *args):
    cursor.callproc(stored_procedure_name, args)
    result = []
    for recordset in cursor.stored_results():
        for row in recordset:
            row = (
                x.strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(x, datetime) else x
                for x in row
            )
            result.append(dict(zip(recordset.column_names, row)))         
    return result


def run_test():
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        print('Auto commit is set to :',cnx.autocommit)
        cnx.autocommit = True 
        print('Auto commit is set to ',cnx.autocommit)
        cursor = None
        try:
            cursor = cnx.cursor(dictionary=True)
            data = call_proc_results(cursor,'stp_test_data', 'HEro')

            cnx.commit()
#        except Exception as e:
 #           print(e)
        finally:
        
            if cursor is not None: cursor.close()
#    print(data,'From db_query')
    return data


def unit_view_unit_metrics(id_user, id_location, id_unit):
    data = []
    print('fetchall unit metric data')
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                f'CALL stp_get_all_unit_level_metrics({id_user}, {id_location}, {id_unit});'
            )
            data = cursor.fetchall()
        finally:
            cursor.close()
    return data
def start_loader():
    data = []
    print('Starting loader')
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                f'CALL stp_test_start_reloader();'
            )
#            data = cursor.fetchall()
        finally:
            cursor.close()
    return "Sucess"

def stop_loader():
    data = []
    print('stoping loader')
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                f'CALL stp_test_stop_reloader();'
            )
#            data = cursor.fetchall()
        finally:
            cursor.close()
    return "Sucess"

def event_runer():
    data = []
    print('fetchall all event data')
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                f'SELECT Event_name FROM INFORMATION_SCHEMA.events;;'
            )
            data = cursor.fetchall()
        finally:
            cursor.close()
    return data


def start_kwh_reloader_process(start_time, end_time):
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        cursor = None
        try:
            print('stp_test_reload_kwh_data Started')
            cursor = cnx.cursor()
            cursor.callproc('stp_test_reload_kwh_data', (start_time, end_time))
            data = cursor.stored_results()
            cnx.commit()
            print('stp_test_reload_kwh_data Completed')
#        except Exception as e:
 #           print(e)
        finally:
        
            if cursor is not None: cursor.close()
    return data

def start_temperature_reloader_process(start_time, end_time):
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        cnx.autocommit = True 
        cursor = None
        try:
            cursor = cnx.cursor()
            print('starting stp_test_reload_temp_data ')
            cursor.callproc('stp_test_reload_temp_data', (start_time, end_time))
            print('stp_test_reload_temp_data Done')
            data = cursor.stored_results()
            cnx.commit()
        except Exception as e:
            print(e)
        finally:
        
            if cursor is not None: cursor.close()
    return data
    
def start_rh_reloader_process(start_time, end_time):
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        cnx.autocommit = True 
        cursor = None
        try:
            cursor = cnx.cursor()
            print('starting stp_test_reload_rh ')
            cursor.callproc('stp_test_reload_rh', (start_time, end_time))
            print('stp_test_reload_rh Done')
            data = cursor.stored_results()
            cnx.commit()
        except Exception as e:
            print(e)
        finally:
        
            if cursor is not None: cursor.close()
    return data




def start_reloader_process(start_time, end_time):
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        cursor = None
        try:
            cursor = cnx.cursor()
            print('starting stp_test_sample ')
            cursor.callproc('stp_test_sample', (start_time, end_time))
            print('stp_test_sample running')
            data = cursor.stored_results()
        finally:
        
            if cursor is not None: cursor.close()
    return data

    

def lock_checker(lock_name):
    query = (
        'SELECT IS_USED_LOCK(%s);'
    )
    try:
        return _db_data(query, (lock_name,))[0][0]
    except IndexError:
        return -1

def _db_data(query, args):
    data = []
    with contextlib.closing(mysql.connector.Connect(**config_conn)) as cnx:
        try:
            cursor = cnx.cursor(prepared=True)
            cursor.execute(query, args)
            data = cursor.fetchall()
        finally:
            cursor.close()
    return data