import hashlib
import base64

class WebSocketFrame:
    def __init__(self, fin_bit, opcode, payload_length, payload):
        self.fin_bit = fin_bit
        self.opcode = opcode
        self.payload_length = payload_length
        self.payload = payload

def compute_accept(websocket_key):
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    new_key = websocket_key + guid
    hashed_key = hashlib.sha1(new_key.encode())
    accept = base64.b64encode(hashed_key.digest()).decode()
    return accept

def parse_ws_frame(websocket_frame_bytes):
    fin_bit = (websocket_frame_bytes[0] & 0b10000000) >> 7
    opcode  = websocket_frame_bytes[0] & 0b00001111
    mask_bit = (websocket_frame_bytes[1] & 0b10000000) >> 7
    payload_length = websocket_frame_bytes[1] & 0b01111111


    if payload_length == 126:
        payload_length = int.from_bytes(websocket_frame_bytes[2:4], byteorder='big')
        payload_idx = 4
    elif payload_length == 127:
        payload_length = int.from_bytes(websocket_frame_bytes[2:10], byteorder='big') 
        payload_idx = 10
    else:
        payload_idx = 2
    if mask_bit == 1:
        masking_key = websocket_frame_bytes[payload_idx:payload_idx+4]
        payload = bytearray(websocket_frame_bytes[payload_idx+4:])
        for i in range(len(payload)):
            payload[i] = payload[i] ^ masking_key[i%4]
    else:
        payload = websocket_frame_bytes[payload_idx:]

    return WebSocketFrame(fin_bit, opcode, payload_length, payload)

def generate_ws_frame(payload):
    payload_bytes_length = len(payload)
    #fin_bit = 1
    #opcode = 0xb0001
    #mask_bit = 0

    if payload_bytes_length < 126:
        frame_begin = bytes([0b10000001, payload_bytes_length])
    elif payload_bytes_length < 65536:
        frame_begin = bytes([0b10000001, 126]) + payload_bytes_length.to_bytes(2, byteorder='big')
    else:
        frame_begin = bytes([0b10000001, 127]) + payload_bytes_length.to_bytes(8, byteorder='big')

    final_frame = frame_begin + payload
    return final_frame 

