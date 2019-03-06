import psycopg2
import os

# import necessary packages
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

try:
    conn = psycopg2.connect("dbname='Proyecto_0' user='equipo5' host='proyecto0.cksq8n4mat8l.us-east-2.rds.amazonaws.com' password='uniandes'")
except(Exception, psycopg2.DatabaseError) as error:
    print("Sin conexión a la base: "+error)


def CambiarEstadoEnBase(id):
    #Cambia estado de la voz en la base
    update_query = "UPDATE concursos_voz SET estado = %s WHERE id = %s"
    cur = conn.cursor()
    try:
        cur.execute(update_query,('C', id))
        conn.commit()
        record = cur.fetchone()
        #updated_rows = cur.rowcount
        print('Registros modificados: '+ record)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()
        #print("se proceso el archivo: {} ".format(archivo[0]))


def ConvertToMP3():

    cur = conn.cursor()
    sql_query = "SELECT id, audio, email FROM concursos_voz WHERE estado = 'P';"
    cur.execute(sql_query)
    archivos_pendientes = cur.fetchall()
    cur.close()

    for archivo in archivos_pendientes:

        #Evalua la extension del archivo
        if archivo[1][-3:] == 'mp3':
            #Copia el archivo ejecutable en destino
            #Toma un archivo mp3 de la carpeta audio y lo copia a la carpeta audio_mp3
            new_mp3_file_name = 'audios_mp3/'+archivo[1].split("/")[1]
            exe_copy = 'cd ..;cp {} {}'.format(archivo[1], new_mp3_file_name)
            
            #Ejecuta la instrucción en el sistema operativo
            os.system(exe_copy)

            #Cambia estado de la voz en la base
            CambiarEstadoEnBase(archivo[0])

        else:
            #Ejecuta la conversion con ffmpeg
            print(archivo[1][:-4].split("/"))
            new_mp3_file_name = 'audios_mp3/'+archivo[1][:-4].split("/")[1]+'.mp3'
            #Armamos el string que ejecuta el ffmpeg en el so
            exe_ffmpeg = 'cd ..; ffmpeg -i {} {}'.format(archivo[1], new_mp3_file_name)
            os.system(exe_ffmpeg)

            #Cambia estado de la voz en la base
            CambiarEstadoEnBase(archivo[0])
        
        # Envía correo avisando que convirtió el archivo
        enviarCorreo(archivo[2])

#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
#Server:smtp.sendgrid.net
#Ports:25, 587(for unencrypted/TLS connections) 465(for SSL connections)
#Username: apikey
#Password: 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

#Server: email-smtp.us-east-1.amazonaws.com
#Ports: 25, 587(for unencrypted/TLS connections) 465(for SSL connections)
#Username: AKIAIOLSEMV7K6G65DBQ
#Password: BG9oT7mP5Rd7iywnLsFns0Eglg8nuOcn27L7ZJPlc9MM
def enviarCorreo(destinatario):   
    # create message object instance
    msg = MIMEMultipart()
    
    message = "Archivo convertido exitosamente !\nGracias por participar"
    host = 'email-smtp.us-east-1.amazonaws.com'
    # setup the parameters of the message
    password = "BG9oT7mP5Rd7iywnLsFns0Eglg8nuOcn27L7ZJPlc9MM"
    smtp_user = "AKIAIOLSEMV7K6G65DBQ"
    msg['From'] = "o.rojasg@uniandes.edu.co"
    msg['To'] = destinatario
    msg['Subject'] = "Audio convertido"
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    #create server
    server = smtplib.SMTP(host=host, port=587)
    
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(smtp_user, password)
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()
    print("successfully sent email to %s:" % (msg['To']))

def main():
    print('Ejecutando convertidor')
    ConvertToMP3() 

if __name__ == "__main__":
    main()