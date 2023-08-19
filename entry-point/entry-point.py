import asyncio
import handler2

import argparse

import time

async def entry_point(args):
    con_handler = handler2.Handler("")
    if not args.ipf:
        server = await asyncio.start_server(con_handler.handle, "::", args.port)
    else:
        print("ipv4/clearnet not suported for now")
        exit()
    #################### open port by upnpy for "clearnet"
    #     try:
    #         import upnpy
    #     except:
    #         print("you need upnpy lib for oppening port in clearnet")
    #         exit()

    #     upnp = upnpy.UPnP()
    #     device = upnp.get_igd()
    #     service = device['WANPPPConnection.1']
    #     service.get_actions()
    #     service.AddPortMapping.get_input_arguments()

    #     import socket
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.connect(("8.8.8.8", 80))
    #     ip = s.getsockname()[0]
    #     s.close()

    #     service.AddPortMapping(
    #         NewRemoteHost='',
    #         NewExternalPort=args.port,
    #         NewProtocol='TCP',
    #         NewInternalPort=args.port,
    #         NewInternalClient=ip,
    #         NewEnabled=1,
    #         NewPortMappingDescription='Test port mapping entry from UPnPy.',
    #         NewLeaseDuration=0
    #     )
    #     server = await asyncio.start_server(con_handler.handle, "0.0.0.0", args.port)

    addrp = server.sockets[0].getsockname()[1]
    print(f'Serving on port {addrp}')
    
    async with server:
        try:
            await server.serve_forever()
        except:
            server.close()
            con_handler.end()
            print()
            exit(0)


def main(args):

    asyncio.run(entry_point(args))



def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument ("-p","--port",default=5363)
    parser.add_argument ("-g", "--gpg-home",default=None ,help="")
    parser.add_argument("-4","--ipf",action="store_true", default=False)

    return parser

if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()

    # print(args)

    main(args)
