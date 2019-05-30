#!/usr/bin/env python

import socket
import wget
import re
import urllib
from urllib import request
import os
import xml.etree.ElementTree as ET


class UPNP:
    is_available = True
    file_name = None
    upnp_url = None
    public_ip_address = None
    port = None
    service_type = ""
    url_base = None

    def __init__(self):
        self.ready()
        self.parse_xml()

    def get_public_address(self, private_ip, port):
        if self.public_ip_address is None:
            self.set_mapping(private_ip, port)
        return self.public_ip_address

    def ready(self):
        try:
            M_SEARCH = 'M-SEARCH * HTTP/1.1\r\n'
            M_SEARCH += 'MX: 3\r\n'
            M_SEARCH += 'HOST: 239.255.255.250:1900\r\n'
            M_SEARCH += 'MAN: "ssdp:discover"\r\n'
            M_SEARCH += 'ST: upnp:rootdevice\r\n'
            M_SEARCH += '\r\n'
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(5)   # 5秒でタイムアウト
            s.bind(('', 1900))
            # M-SEARCHをマルチキャストする
            s.sendto(M_SEARCH.encode('utf-8'), ('239.255.255.250', 1900))
            response = ""
            while True:
                try:
                    filename = 'upnp.xml'
                    # os.remove(filename)
                    response, address = s.recvfrom(8192)
                    print('from', address)
                    print(response)
                    print('=' * 40)
                    response = response.decode('utf-8')
                    print(response)
                    url_pattern = 'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+'
                    url = re.findall(url_pattern, response)[0]
                    self.file_name = wget.download(url, out=filename)
                    try:
                        url_base_pattern = 'https?://[\w:%#\$&\?\(\)~\.=\+\-]+'
                        self.url_base = re.findall(url_base_pattern, response)[0]
                    except:
                        pass
                    break
                except socket.timeout:  # タイムアウトしたときの処理
                    print('time out')
                    break
        except Exception as e:
            self.is_available = False
            print(e)
        finally:
            s.close()

    def parse_xml(self):
        print(self.is_available)
        if self.is_available is False:
            return
        try:
            tree = ET.parse(self.file_name)
            root = tree.getroot()
            url_base_text = root.find('{urn:schemas-upnp-org:device-1-0}URLBase')
            if url_base_text is not None:
                self.url_base = url_base_text.text
            # print(url_base)
            self.is_available = False
            for service in root.findall('.//{urn:schemas-upnp-org:device-1-0}service'):
                service_type = service.find('{urn:schemas-upnp-org:device-1-0}serviceType')
                print(service_type.text)
                if service_type is None:
                    continue
                if service_type.text == 'urn:schemas-upnp-org:service:WANPPPConnection:1':
                    self.service_type = 'WANPPPConnection'
                elif service_type.text == 'urn:schemas-upnp-org:service:WANIPConnection:1':
                    self.service_type = 'WANIPConnection'
                else:
                    continue

                control_url = service.find('{urn:schemas-upnp-org:device-1-0}controlURL')
                print(control_url.text)
                if control_url is None:
                    continue
                self.upnp_url = self.url_base + control_url.text
                print(self.upnp_url)
                self.is_available = True
                break
        except Exception as e:
            print(e)
            self.is_available = False

    # wan側の確認
    def confirm_wan(self):
        if self.is_available is False:
            return
        SOAP = '<?xml version="1.0"?>\r\n'
        SOAP += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\r\n'
        SOAP += '<s:Body>\r\n'
        SOAP += '<u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:service:{0}:1">\r\n'.format(self.service_type)
        SOAP += '</u:GetExternalIPAddress>\r\n'
        SOAP += '</s:Body>\r\n'
        SOAP += '</s:Envelope>\r\n'

        req = request.Request(self.upnp_url)
        req.add_header('Content-Type', 'text/xml; charset="utf-8"')
        req.add_header('SOAPACTION', '"urn:schemas-upnp-org:service:{0}:1#GetExternalIPAddress"'.format(self.service_type))
        req.data = SOAP.encode('utf-8')

        res = request.urlopen(req)

        # print(res.read().decode('utf-8'))
        xml = res.read().decode('utf-8')
        root = ET.fromstring(xml)
        self.public_ip_address = root.find('.//NewExternalIPAddress').text
        print(self.public_ip_address)

    # mappingの確認
    def confirm_mapping(self):
        if self.is_available is False:
            return
        ID = 0
        while True:
            SOAP  = '<?xml version="1.0"?>\r\n'
            SOAP += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\r\n'
            SOAP += '<s:Body>\r\n'
            SOAP += '<m:GetGenericPortMappingEntry xmlns:m="urn:schemas-upnp-org:service:{0}:1">\r\n'.format(self.service_type)
            SOAP += '<NewPortMappingIndex>' + str(ID) + '</NewPortMappingIndex>\r\n'
            SOAP += '</m:GetGenericPortMappingEntry>\r\n'
            SOAP += '</s:Body>\r\n'
            SOAP += '</s:Envelope>\r\n'

            req = request.Request(self.upnp_url)
            req.add_header('Content-Type', 'text/xml; charset="utf-8"')
            req.add_header('SOAPACTION', '"urn:schemas-upnp-org:service:{0}:1#GetGenericPortMappingEntry"'.format(self.service_type))
            req.data = SOAP.encode('utf-8')

            try:
                res = request.urlopen(req)
                print(res.read())
            except Exception as e:
                print(e)
                break
            print('=' * 40)
            ID += 1

    # mappingの設定
    def set_mapping(self, private_ip, port):
        if self.is_available is False:
            return
        NEW_EXTERNAL_PORT = port   # WAN側のポート番号
        NEW_INTERNAL_PORT = port   # 転送先ホストのポート番号
        NEW_INTERNAL_CLIENT = private_ip   # 転送先ホストのIPアドレス
        NEW_PROTOCOL = 'TCP'
        LEASE_DURATION = '0'    # 設定の有効期間(秒)。0のときは無期限
        DESCRIPTION = 'test'

        SOAP = '<?xml version="1.0"?>\r\n'
        SOAP += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\r\n'
        SOAP += '<s:Body>\r\n'
        SOAP += '<m:AddPortMapping xmlns:m="urn:schemas-upnp-org:service:{0}:1">\r\n'.format(self.service_type)
        SOAP += '<NewRemoteHost></NewRemoteHost>\r\n'
        SOAP += '<NewExternalPort>' + str(NEW_EXTERNAL_PORT) + '</NewExternalPort>\r\n'
        SOAP += '<NewProtocol>' + NEW_PROTOCOL + '</NewProtocol>\r\n'
        SOAP += '<NewInternalPort>' + str(NEW_INTERNAL_PORT) + '</NewInternalPort>\r\n'
        SOAP += '<NewInternalClient>' + NEW_INTERNAL_CLIENT + '</NewInternalClient>\r\n'
        SOAP += '<NewEnabled>1</NewEnabled>\r\n'
        SOAP += '<NewPortMappingDescription>' + DESCRIPTION + '</NewPortMappingDescription>\r\n'
        SOAP += '<NewLeaseDuration>' + LEASE_DURATION + '</NewLeaseDuration>\r\n'
        SOAP += '</m:AddPortMapping>\r\n'
        SOAP += '</s:Body>\r\n'
        SOAP += '</s:Envelope>\r\n'

        req = request.Request(self.upnp_url)
        req.add_header('Content-Type', 'text/xml; charset="utf-8"')
        req.add_header('SOAPACTION', '"urn:schemas-upnp-org:service:{0}:1#AddPortMapping"'.format(self.service_type))
        req.data = SOAP.encode('utf-8')

        try:
            res = request.urlopen(req)
            print(res.read())
        except Exception as e:
            print('register: {}'.format(e))

    # 設定の削除
    def delete_mapping(self):
        if self.is_available is False:
            return
        if self.port is None:
            return
        NEW_EXTERNAL_PORT = self.port
        NEW_PROTOCOL = 'TCP'

        SOAP  = '<?xml version="1.0"?>\r\n'
        SOAP += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\r\n'
        SOAP += '<s:Body>\r\n'
        SOAP += '<m:DeletePortMapping xmlns:m="urn:schemas-upnp-org:service:{0}:1">\r\n'.format(self.service_type)
        SOAP += '<NewRemoteHost></NewRemoteHost>\r\n'
        SOAP += '<NewExternalPort>' + str(NEW_EXTERNAL_PORT) + '</NewExternalPort>\r\n'
        SOAP += '<NewProtocol>' + NEW_PROTOCOL + '</NewProtocol>\r\n'
        SOAP += '</m:DeletePortMapping>\r\n'
        SOAP += '</s:Body>\r\n'
        SOAP += '</s:Envelope>\r\n'

        req = request.Request(self.upnp_url)
        req.add_header('Content-Type', 'text/xml; charset="utf-8"')
        req.add_header('SOAPACTION', '"urn:schemas-upnp-org:service:{0}:1#DeletePortMapping"'.format(self.service_type))
        req.data = SOAP.encode('utf-8')

        try:
            res = request.urlopen(req)
            print(res.read())
        except Exception as e:
            print('delete{}'.format(e))


#
# from utility import get_local_address
# upnp = UPNP()
# upnp.confirm_wan()
# upnp.confirm_mapping()
# print(get_local_address())
# # upnp.set_mapping(get_local_address(), 5000)
# upnp.delete_mapping()
