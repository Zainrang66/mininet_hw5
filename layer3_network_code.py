
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
        self.addLink(router_A, router_B, intfName1='ra-eth1', params1={'ip': '20.10.100.1/30'}, intfName2='rb-eth1',
                    params2={'ip': '20.10.100.2/30'})
        # link router A to router C
        self.addLink(router_A, router_C, intfName1='ra-eth2', params1={'ip': '20.10.100.5/30'}, intfName2='rc-eth1',
                    params2={'ip': '20.10.100.6/30'})
        # link router C to router B
        self.addLink(router_B, router_C, intfName1='rb-eth2', params1={'ip': '20.10.100.9/30'}, intfName2='rc-eth2',
                    params2={'ip': '20.10.100.10/30'})
        
import time

def run():

    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=Controller)

    info('*** Starting network\n')
    net.start()

    # give the network a moment to fully initialize
    time.sleep(1)

    router_A = net.get('router_A')
    router_B = net.get('router_B')
    router_C = net.get('router_C')

    host_A_1 = net.get('host_A_1')
    host_A_2 = net.get('host_A_2')
    host_B_1 = net.get('host_B_1')
    host_B_2 = net.get('host_B_2')
    host_C_1 = net.get('host_C_1')
    host_C_2 = net.get('host_C_2')

    # ------------------------------------------------------------------
    # Task 3 -- static routes on each router
    # ------------------------------------------------------------------
    info('*** Adding routes on Router A\n')
    # Router A is directly on LAN A (20.10.172.128/26)
    # It needs routes to LAN B and LAN C through its inter-router interfaces
    print(router_A.cmd('ip route add 20.10.172.0/25   via 20.10.100.2 dev ra-eth1'))
    print(router_A.cmd('ip route add 20.10.172.192/27 via 20.10.100.6 dev ra-eth2'))

    info('*** Adding routes on Router B\n')
    # Router B is directly on LAN B (20.10.172.0/25)
    # It needs routes to LAN A and LAN C through its inter-router interfaces
    print(router_B.cmd('ip route add 20.10.172.128/26 via 20.10.100.1 dev rb-eth1'))
    print(router_B.cmd('ip route add 20.10.172.192/27 via 20.10.100.10 dev rb-eth2'))

    info('*** Adding routes on Router C\n')
    # Router C is directly on LAN C (20.10.172.192/27)
    # It needs routes to LAN A and LAN B through its inter-router interfaces
    print(router_C.cmd('ip route add 20.10.172.128/26 via 20.10.100.5 dev rc-eth1'))
    print(router_C.cmd('ip route add 20.10.172.0/25   via 20.10.100.9 dev rc-eth2'))

    # ------------------------------------------------------------------
    # Task 3 -- static routes on each host
    # The hosts already have a default route to their local router,
    # but we add explicit routes to be safe
    # ------------------------------------------------------------------
    info('*** Adding routes on hosts\n')
    print(host_A_1.cmd('ip route add 20.10.172.0/25   via 20.10.172.190'))
    print(host_A_1.cmd('ip route add 20.10.172.192/27 via 20.10.172.190'))
    print(host_A_2.cmd('ip route add 20.10.172.0/25   via 20.10.172.190'))
    print(host_A_2.cmd('ip route add 20.10.172.192/27 via 20.10.172.190'))

    print(host_B_1.cmd('ip route add 20.10.172.128/26 via 20.10.172.126'))
    print(host_B_1.cmd('ip route add 20.10.172.192/27 via 20.10.172.126'))
    print(host_B_2.cmd('ip route add 20.10.172.128/26 via 20.10.172.126'))
    print(host_B_2.cmd('ip route add 20.10.172.192/27 via 20.10.172.126'))

    print(host_C_1.cmd('ip route add 20.10.172.128/26 via 20.10.172.222'))
    print(host_C_1.cmd('ip route add 20.10.172.0/25   via 20.10.172.222'))
    print(host_C_2.cmd('ip route add 20.10.172.128/26 via 20.10.172.222'))
    print(host_C_2.cmd('ip route add 20.10.172.0/25   via 20.10.172.222'))

    # verify the routes actually got added this time
    info('*** Routing tables after configuration\n')
    info('Router A:\n')
    info(router_A.cmd('ip route'))
    info('Router B:\n')
    info(router_B.cmd('ip route'))
    info('Router C:\n')
    info(router_C.cmd('ip route'))

    info('*** Testing with pingAll\n')
    net.pingAll()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()