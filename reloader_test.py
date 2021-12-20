from data_access import db_queries
from shared import mailer
from flask_restful import Resource, abort
import datetime
import time

class Logger():
    def __init__(self):
#        self.log_file=f"/root/genesis/GenesisServer/wm_server.log"
        self.log_file=f"/root/genesis/GenesisServer/tests/mysql/log/log_file.log"
        
    def append_reloader_info_log(self, message):
        with open(self.log_file, mode="a+") as wm_log_file:
            data = wm_log_file.read().split("\n")
            data.append(f"{str(datetime.datetime.now())} :[Reloader][INFO]: {message}")
            wm_log_file.write("\n".join(data))
    
    def append_reloader_failer_log(self,message):
        with open(self.log_file, mode="a+") as wm_log_file:
            data = wm_log_file.read().split("\n")
            data.append(f"{str(datetime.datetime.now())} :[Reloader][Failed]: {message}")
            wm_log_file.write("\n".join(data))
        
class Mailer():
    def __init__(self):
        self.loger=Logger()
        
    def write_email(self, body, level='Failer',subject='No Sub' ):
        body=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S : ')+body
        subject='Reloader Task - '+level+' - '+subject    
#        level="Failer" #j
        try:
            self.loger.append_reloader_info_log(f'Sending Email with text \n{body}\n')
            mailer.send_mail(level,subject,body,attach_svlog=False)
        except Exception as e:
            self.loger.append_reloader_failer_log(f'Mailer Failed While sending Email with Exception: {e}\n{body}')
#        mailer.test(level,subject,body,False)
        # for line in body.split("\n"):
        #     print(line)


class Reloader(Resource):
    def __init__(self):
        self.loger=Logger()
        self.mailer=Mailer()

    def get_numeric_lock_id(self,lock_):               
        lock_id = db_queries.lock_checker(lock_)       
        if lock_id ==None:
            return None
        else:
            return lock_id

    def start_event_loader(self):
        data=db_queries.start_loader()
        return data
        
    def stop_event_loader(self):
        data=db_queries.stop_loader()
        return data
    
    def get_runing_event(self):               
        data = db_queries.event_runer()
        events=[]        
        if data ==None:
            return None
        else:
            for event in data:
                events.append(event['EVENT_NAME'])
            return events
    
    def run_kwh_reloader(self,start_time,end_time):
        try:
            return db_queries.start_kwh_reloader_process(start_time,end_time)
        except Exception as e:
            self.loger.append_reloader_failer_log(f'KWH Reloader Failed with Exception: {e}')
            self.mailer.write_email(f'KWH Loader Failed with Exception: {e}','Failer','KWH Failed')
            
    def run_rh_reloader(self,start_time,end_time):
        try:
            return db_queries.start_rh_reloader_process(start_time,end_time)
        except Exception as e:
            self.loger.append_reloader_failer_log(f'RH Reloader Failed with Exception: {e}')
            self.mailer.write_email(f'RH Loader Failed with Exception: {e}','Failer','RH Failed')

    def run_temperature_reloader(self,start_time,end_time):
        try:
            return db_queries.start_temperature_reloader_process(start_time,end_time)
        except Exception as e:
            self.loger.append_reloader_failer_log(f'Temperature Reloader Failed with Exception: {e}')
            self.mailer.write_email(f'Temperature Loader Failed with Exception: {e}','Failer','Temperature Failed')
    
    def stop_loader(self):
        numeric=True
        boolean=True
        self.loger.append_reloader_info_log('Started loader stoping process')
        while numeric:        
            self.stop_event_loader()
#            events=self.get_runing_event()
            run_id=self.get_numeric_lock_id('lock_stp_load_data')
            if run_id == None:
                self.loger.append_reloader_info_log('Numeric loader has been stoped')
#               print("Numeric Loader Stoped")
                numeric=False
            else:
                self.loger.append_reloader_info_log(f'Numeric loader is Running with id:{run_id}')
#                print("Numeric Loader Running")
            time.sleep(5)
        while boolean:        
            self.stop_event_loader()
#            events=self.get_runing_event()
            run_id=self.get_numeric_lock_id('lock_stp_load_data_boolean')
#            print(run_id)
            if run_id == None:
 #               print("boolean Loader Stoped")
                self.loger.append_reloader_info_log('Boolean loader Stoped')
                boolean=False
            else:
                self.loger.append_reloader_info_log(f'Boolean loader Running with id: {run_id}')
  #              print("boolean Loader Running")
            time.sleep(2)

    def start_loader(self):
        numeric=True
        boolean=True

        while numeric:        
            self.start_event_loader()
            time.sleep(5)
            events=self.get_runing_event()
            data=self.get_numeric_lock_id('lock_stp_load_data')
#            print(data)
            if data != None:
 #               print("Numeric Loader Stoped")
                numeric=False
            else:
                pass
  #              print("Numeric Loader Running")

        while boolean:        
            self.start_event_loader()
            time.sleep(5)
            events=self.get_runing_event()
            data=self.get_numeric_lock_id('lock_stp_load_data_boolean')
#            print(data)
            if data != None:
 #               print("boolean Loader Stoped")
                boolean=False
            else:
                pass
  #              print("boolean Loader Running")
    
                    
    def run_test_proc(self):
        data=db_queries.run_test()
#        print(data)
        pass
    
    def run_all_reloader_task(self,start_time,end_time):
        try:
            self.stop_loader()
            self.loger.append_reloader_info_log(f'Starting KWH reloader between : {start_time} to {end_time}')
            self.run_kwh_reloader(start_time,end_time)
            self.loger.append_reloader_info_log(f'Starting RH reloader between : {start_time} to {end_time}')
            self.run_rh_reloader(start_time,end_time)
            self.loger.append_reloader_info_log(f'Starting Temperature reloader between : {start_time} to {end_time}')
            self.run_temperature_reloader(start_time,end_time)
            self.loger.append_reloader_info_log(f'Starting loader')
            self.start_event_loader()
            self.mailer.write_email(f'loader Process completed successfully','Sucess','Completed')
        except Exception as e:
            self.mailer.write_email(f'Reloader Process Failed with unhandled error : {e}','INFO','Unhandled Failed')


def main():
    reloader=Reloader()
    start_time = datetime.datetime.now()
    end_time= start_time - datetime.timedelta(days=3)
    
    start_time=start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time=end_time.strftime('%Y-%m-%d %H:%M:%S')

    #    print(start_time, ': Format = ',type(start_time))
    #   print(end_time, ': Format = ',type(end_time))    
    reloader.run_all_reloader_task('2021-12-13 00:00:00','2021-12-17 17:00:00')
    


if __name__== "__main__":
    main()