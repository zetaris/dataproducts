#!/usr/local/bin/python3

'''
'''


from grpc import secure_channel
import jaydebeapi

# jdbc:zetaris:clouddatafabric@nycdata.5e3fe4a3.datafabric.zetaris.com/RestClient=https

# https://nycdata-ui.5e3fe4a3.datafabric.zetaris.com/lightning-gui/


# vdw connection
uid = "stephen.anthony@datamesh.com"
pwd = "Passw0rd!"
driver_class = "com.zetaris.lightning.jdbc.LightningDriver"
driver_file = "../../driver/ndp-jdbc-driver-2.1.0.12-driver.jar"
connection_string= 'jdbc:zetaris:clouddatafabric@nycdata.5e3fe4a3.datafabric.zetaris.com/RestClient=https'
#connection_string='jdbc:zetaris:lightning@'+ host + '/RestClient=https'


#con = jaydebeapi.connect(driver_class, connection_string, {'user':uid, 'password':pwd}, driver_file)

con = jaydebeapi.connect(driver_class, connection_string, {'user':uid, 'password':pwd}, driver_file)
curs = con.cursor()


# total tests
sql_str = "select * from NY_WEATHER.nyc_weather LIMIT 10"
# sql_str = "select * from Z_NY_FLIGHT_TRACKER LIMIT 1"
curs.execute(sql_str)
result = curs.fetchall()
print(result)



