from locust import HttpUser, task, events
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os

from locust_influxdb_listener import InfluxDBListener, InfluxDBSettings

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """
    Hook event that enables starting an influxdb connection
    """
    # this settings matches the given docker-compose file
    influxDBSettings = InfluxDBSettings(
        influx_host = 'localhost',
        influx_port = '8086',
        user = 'admin',
        pwd = 'pass',
        database = 'music_converter'
    )
    # start listerner with the given configuration
    InfluxDBListener(env=environment, influxDbSettings=influxDBSettings)


class MusicConverterLoadTest(HttpUser):

    @task
    def login_and_send_conversion(self):
        headers1 = {'Content-Type':'application/json'}
        body = data=json.dumps({"username":"luis", "password":"123"})
        response = self.client.post("/api/auth/login", data=body, headers=headers1)
        data = response.json()
        #print("response-login==>", data)
        bearer_token = 'Bearer ' + data['token']

        mp3_filename = os.path.basename('test2.mp3')
        m = MultipartEncoder(
                fields={'newFormat': 'mp3',
                'fileName': (mp3_filename, open('test2.mp3', 'rb'), 'audio/mpeg')}
            )

        headers = {'Content-Type': m.content_type, 'Authorization':bearer_token}
        response2 = self.client.post("/api/tasks", data=m, headers=headers)
        data2 = response2.json()
        #print("response-task==>", data2)

    def on_start(self):
        print("Starting locust....")
