import asyncio
import ipaddress
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def send_initial_message(websocket: WebSocket):
    await asyncio.sleep(0.5)
    await websocket.send_text("I'm your subnet helper bot. Feel free to ask networking questions.")
    await asyncio.sleep(0.5)
    await websocket.send_text('Type "Start" to begin')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    asyncio.create_task(send_initial_message(websocket))
    buttons_created = False

    while True:
        user_input = await websocket.receive_text()
        subnet_output = process_user_input(user_input)

        await websocket.send_text(subnet_output)

        if user_input.lower() == 'flsm':
           # await websocket.send_text("Please enter the IP address you wish to subnet:")
            ip_address = await websocket.receive_text()

            await websocket.send_text("Please enter the number of hosts:")
            num_hosts = int(await websocket.receive_text())

            subnet_info = calculate_subnet(ip_address, num_hosts)
            response_message = "\n".join([f"{key}: {value}" for key, value in subnet_info.items()])
            await websocket.send_text(response_message)
            await websocket.send_text('Do you want to try again?')

def process_user_input(user_input: str) -> str:
    # Implement your subnet FLSM logic here
    # Example: Extract IP and host information and calculate subnet mask
    # Replace this with your specific logic based on your requirements
    if user_input.lower() == 'start':
        return "Great! Click 'Fixed Length Subnet' or 'What is FLSM?' to proceed."

    # Nested check for 'flsm' and 'vlsm'
    elif user_input.lower() == 'flsm':
        return "I see enter IP address you wish to subnet"
    elif user_input.lower() == 'vlsm':
        return "FLSM, or Fixed-Length Subnet Masking, is a subnetting approach in networking where each subnet contains an equal number of IP addresses. It involves dividing an IP network into subnetworks with a consistent number of hosts per subnet. While FLSM is straightforward, it may lead to inefficient use of IP addresses compared to more flexible approaches like VLSM (Variable-Length Subnet Masking)."
    else:
        return "I didn't get that"

def calculate_subnet(ip_address, num_hosts):
    try:
        ip = ipaddress.IPv4Address(ip_address)
        subnet_mask = ipaddress.IPv4Network(f'{ip}/{32 - (num_hosts).bit_length()}', strict=False).netmask
        network = ipaddress.IPv4Network(f'{ip}/{subnet_mask}', strict=False)

        return {
            'Subnet Mask': subnet_mask,
            'Network Address': network.network_address,
            'First Address': network.network_address + 1,
            'Last Address': network.broadcast_address - 1,
            'Broadcast Address': network.broadcast_address
        }

    except ValueError as e:
        return {'Error': str(e)}
