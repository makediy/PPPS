"""
The MIT License (MIT)
Copyright © 2020 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/esp32-ble-uart
Original repo: https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_peripheral.py
"""
import tryi2c
import ubluetooth as bt
import time
__UART_UUID = bt.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
__RX_UUID = bt.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
__TX_UUID = bt.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

__UART_SERVICE = (
	__UART_UUID,
	(
		(__TX_UUID, bt.FLAG_NOTIFY,),
		(__RX_UUID, bt.FLAG_WRITE,),
	),
)


class BLEUART:
	def __init__(self, ble, rx_callback=None, name="PPPS", rxbuf=100):
		self.__ble = ble
		self.__rx_cb = rx_callback
		self.__conn_handle = None

		self.__write = self.__ble.gatts_write
		self.__read = self.__ble.gatts_read
		self.__notify = self.__ble.gatts_notify

		self.__ble.active(False)
		print("activating ble...")
		self.__ble.active(True)
		print("ble activated")

		self.__ble.config(rxbuf=rxbuf)
		self.__ble.irq(self.__irq)
		self.__register_services()

		self.__adv_payload = BLETools.advertising_generic_payload(
			services=(__UART_UUID,),
			appearance=BLEConst.Appearance.GENERIC_COMPUTER,
		)
		self.__resp_payload = BLETools.advertising_resp_payload(
			name=name
		)

		self.__advertise()

	def __register_services(self):
		(
			(
				self.__tx_handle,
				self.__rx_handle,
			),
		) = self.__ble.gatts_register_services((__UART_SERVICE,))

	def __advertise(self, interval_us=500000):
		self.__ble.gap_advertise(None)
		self.__ble.gap_advertise(interval_us, adv_data=self.__adv_payload, resp_data=self.__resp_payload)
		print("advertising...")
    #中断请求
	def __irq(self, event, data):
		if event == BLEConst.IRQ.IRQ_CENTRAL_CONNECT:
			self.__conn_handle, addr_type, addr, = data
			print("[{}] connected, handle: {}".format(BLETools.decode_mac(addr), self.__conn_handle))

			self.__ble.gap_advertise(None)
		elif event == BLEConst.IRQ.IRQ_CENTRAL_DISCONNECT:
			self.__conn_handle, _, addr, = data
			print("[{}] disconnected, handle: {}".format(BLETools.decode_mac(addr), self.__conn_handle))

			self.__conn_handle = None
			self.__advertise()
		elif event == BLEConst.IRQ.IRQ_GATTS_WRITE:
			conn_handle, value_handle = data

			if conn_handle == self.__conn_handle and value_handle == self.__rx_handle:
				if self.__rx_cb:
					self.__rx_cb(self.__read(self.__rx_handle))

	def send(self, data):
		"""
		将数据写入本地缓存，并推送到中心设备
		"""
		self.__write(self.__tx_handle, data)

		if self.__conn_handle is not None:
			self.__notify(self.__conn_handle, self.__tx_handle, data)
			

#从tools.py中摘取。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
import struct
from ubluetooth import UUID
PACK = struct.pack
UNPACK = struct.unpack

class BLETools(object):
	"""
	Payload Generator Functions
	"""
	# Advertising payloads are repeated packets of the following form:
	#   1 byte data length (N + 1)
	#   1 byte type (see constants below)
	#   N bytes type-specific data
	@staticmethod
	def advertising_generic_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
		"""
		Generate a payload to be passed to gap_advertise(adv_data=...).
		"""
		payload = bytearray()

		def _append(adv_type, value):
			nonlocal payload
			payload += PACK('BB', len(value) + 1, adv_type) + value

		_append(BLEConst.ADType.AD_TYPE_FLAGS, PACK('B', (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))

		if name:
			_append(BLEConst.ADType.AD_TYPE_COMPLETE_LOCAL_NAME, name)

		if services:
			for uuid in services:
				b = bytes(uuid)
				if len(b) == 2:
					_append(BLEConst.ADType.AD_TYPE_16BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 4:
					_append(BLEConst.ADType.AD_TYPE_32BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 16:
					_append(BLEConst.ADType.AD_TYPE_128BIT_SERVICE_UUID_COMPLETE, b)

		# See org.bluetooth.characteristic.gap.appearance.xml
		_append(BLEConst.ADType.AD_TYPE_APPEARANCE, PACK('<h', appearance))

		return payload

	@staticmethod
	def advertising_resp_payload(name=None, services=None):
		"""
		Generate payload for Scan Response
		"""
		payload = bytearray()

		def _append(adv_type, value):
			nonlocal payload
			payload += PACK('BB', len(value) + 1, adv_type) + value

		if name:
			_append(BLEConst.ADType.AD_TYPE_COMPLETE_LOCAL_NAME, name)

		if services:
			for uuid in services:
				b = bytes(uuid)
				if len(b) == 2:
					_append(BLEConst.ADType.AD_TYPE_16BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 4:
					_append(BLEConst.ADType.AD_TYPE_32BIT_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 16:
					_append(BLEConst.ADType.AD_TYPE_128BIT_SERVICE_UUID_COMPLETE, b)

		return payload

	@staticmethod
	def decode_mac(addr):
		"""
		Decode readable mac address from advertising addr
		"""
		if isinstance(addr, memoryview):
			addr = bytes(addr)

		assert isinstance(addr, bytes) and len(addr) == 6, ValueError("mac address value error")
		return ":".join(['%02X' % byte for byte in addr])
	


#从const.py中摘取。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
from micropython import const

class BLEConst(object):
	class IRQ(object):
		IRQ_CENTRAL_CONNECT = const(1)
		IRQ_CENTRAL_DISCONNECT = const(2)
		IRQ_GATTS_WRITE = const(3)
		
		
	class Appearance(object):
		Unknown = const(0) # None
		GENERIC_PHONE = const(64) # Generic category
		GENERIC_COMPUTER = const(128) # Generic category


	class ADType(object):
		'''
		Advertising Data Type
		'''
		AD_TYPE_FLAGS = const(0x01) # Flags for discoverability.
		AD_TYPE_16BIT_SERVICE_UUID_COMPLETE = const(0x03) # Complete list of 16 bit service UUIDs.
		AD_TYPE_32BIT_SERVICE_UUID_COMPLETE = const(0x05) # Complete list of 32 bit service UUIDs.
		AD_TYPE_128BIT_SERVICE_UUID_COMPLETE = const(0x07) # Complete list of 128 bit service UUIDs.
		AD_TYPE_COMPLETE_LOCAL_NAME = const(0x09) # Complete local device name.
		AD_TYPE_APPEARANCE = const(0x19) # Appearance. 


flag=0
from machine import Pin
def rx_callback(data):
    global flag
    print("rx received: {}".format(data))
    if data!=None:
        if data.find(b'\x08\x08\x08\x08\x08\x08\x08\x08')!=-1:
            flag=1
        elif data.find(b'\x01\x02')!=-1:
            flag=1
            tryi2c.sc.Output_Voltage_Setting(data[2]+data[3]/100.0)
        elif data.find(b'\x01\x03')!=-1:
            flag=1
            tryi2c.sc.Output_Current_Limit(data[2]+data[3]/100.0)
        else:flag=0
    else:
        pass


ble = bt.BLE()
uart = BLEUART(ble, rx_callback)


while 1:
    if flag==1:
        tryi2c.sc.readall(0)
        # print('aVin',tryi2c.aVin.read_uv()/1000000.0*11)
#         print('aVout',tryi2c.aVout.read_uv()/1000000.0*11)
#         print('aIout',tryi2c.aIout.read_uv()/1000.0*2/640)
        #print('a2V5',tryi2c.a2V5.read_uv()/1000000)
        s=bytearray(10)
        s[0]=int((tryi2c.aVin.read_uv()/1000000.0*11)//1)
        s[1]=int(((tryi2c.aVin.read_uv()/1000000.0*11)%1)*100)
        s[2]=int((tryi2c.aVout.read_uv()/1000000.0*11)//1)
        s[3]=int(((tryi2c.aVout.read_uv()/1000000.0*11)%1)*100)
        s[4]=int((tryi2c.aIout.read_uv()/1000.0*2/640)//1)
        s[5]=int(((tryi2c.aIout.read_uv()/1000.0*2/640)%1)*100)
        s[6]=int(tryi2c.sc.IOUT_ILIM//1)
        s[7]=int(((tryi2c.sc.IOUT_ILIM)%1)*100)
        s[8]=int(tryi2c.sc.VINREG_FLAG)
        s[9]=int((tryi2c.sc.IBUS_FLAG))
        uart.send(s)
        time.sleep(0.2)
