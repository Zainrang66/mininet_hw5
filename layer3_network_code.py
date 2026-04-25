
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter( Node ):

    def config( self, **params ):
        super( LinuxRouter, self).config(**params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo(Topo):
    
    def build(self):
        info('*** Adding routers\n')
        router_A = self.addHost('router_A', cls=LinuxRouter, ip=None)
        router_B = self.addHost('router_B', cls=LinuxRouter, ip=None)
        router_C = self.addHost('router_C', cls=LinuxRouter, ip=None)

        info('*** Adding hosts\n')
        host_A_1 = self.addHost('host_A_1', ip='20.10.172.129/26', defaultRoute='via 20.10.172.190')
        host_A_2 = self.addHost('host_A_2', ip='20.10.172.130/26', defaultRoute='via 20.10.172.190')
        host_B_1 = self.addHost('host_B_1', ip='20.10.172.1/25', defaultRoute='via 20.10.172.126')
        host_B_2 = self.addHost('host_B_2', ip='20.10.172.2/25', defaultRoute='via 20.10.172.126')
        host_C_1 = self.addHost('host_C_1', ip='20.10.172.194/27', defaultRoute='via 20.10.172.222')
        host_C_2 = self.addHost('host_C_2', ip='20.10.172.195/27', defaultRoute='via 20.10.172.222')

        # each LAN needs a switch so both hosts can connect to the router
        info('*** Adding switches\n')
        sA = self.addSwitch('sA', dpid='0000000000000001')
        sB = self.addSwitch('sB', dpid='0000000000000002')
        sC = self.addSwitch('sC', dpid='0000000000000003')

        info('*** Adding links\n')
        self.addLink(router_A, sA, intfName1='ra-eth0', params1={'ip': '20.10.172.190/26'})
        self.addLink(host_A_1, sA)
        self.addLink(host_A_2, sA)
        self.addLink(router_B, sB, intfName1='rb-eth0', params1={'ip': '20.10.172.126/25'})
        self.addLink(host_B_1, sB)
        self.addLink(host_B_2, sB)
        self.addLink(router_C, sC, intfName1='rc-eth0', params1={'ip': '20.10.172.222/27'})
        self.addLink(host_C_1, sC)
        self.addLink(host_C_2, sC)
        # link router A to router B
        self.addLink(router_A, router_B, intfName1='ra-eth1', params1={'ip': '20.10.100.1/24'}, intfName2='rb-eth1',
                    params2={'ip': '20.10.100.2/24'})
        # link router A to router C
        self.addLink(router_A, router_C, intfName1='ra-eth2', params1={'ip': '20.10.100.3/24'}, intfName2='rc-eth1',
                    params2={'ip': '20.10.100.4/24'})
        # link router C to router B
        self.addLink(router_B, router_C, intfName1='rb-eth2', params1={'ip': '20.10.100.5/24'}, intfName2='rc-eth2',
                    params2={'ip': '20.10.100.6/24'})
        
def run():

    topo = NetworkTopo()
    net = Mininet(topo=topo)

    info('*** Start\n')
    net.start()

    router_A = net.get('router_A')
    router_B = net.get('router_B')
    router_C = net.get('router_C')

    info('*** Router A interfaces:\n')
    info(router_A.cmd('ip addr'))
    info('*** Router B interfaces:\n')
    info(router_B.cmd('ip addr'))
    info('*** Router C interfaces:\n')
    info(router_C.cmd('ip addr'))

    info('*** Testing using pingAll\n')
    net.pingAll()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stop')
    net.stop()



if __name__ == '__main__':
    setLogLevel( 'info' )
    run()