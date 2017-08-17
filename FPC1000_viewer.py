#!/usr/bin/env python

# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import argparse, numpy, pyqtgraph, socket, sys

#==============================================================================

# Default filename
IP = '192.168.0.11'
PORT = 5555

#==============================================================================

def parse():
    """
    Specific parsing procedure for Allan Deviation plotting tool.
    :returns: populated namespace (parser)
    """
    parser = argparse.ArgumentParser(description = 'R&S FPC1000 spectrum viewer',
                                     epilog = 'Example: \'./FPC1000_viewer.py -ip \'192.168.0.2\' -p 1234\' plot current spectrum from given device')

    parser.add_argument('-ip',
                        action='store',
                        dest='ip',
                        default=IP,
                        help='device IP (default '+IP+')')

    parser.add_argument('-p',
                        action='store',
                        dest='port',
                        default=PORT,
                        help='device port (default '+str(PORT)+')')

    args = parser.parse_args()
    return args

#==============================================================================

def send(sock, command):
    sock.send("%s\n"%command)

#==============================================================================

def read(sock):
    ans = ''
    nb_data_list = []
    nb_data = ''
    try:
        while ans != '\n':
            ans = sock.recv(1)
            nb_data_list.append(ans) # Return the number of data
        list_size = len(nb_data_list)
        for j in range (0, list_size):
            nb_data = nb_data+nb_data_list[j]
        return nb_data
    except socket.timeout:
        print "Socket timeout error when reading."

#==============================================================================

def get_spectrum(sock):
    send(sock, 'FREQ:STAR?')
    x1 = read(sock)
    x1 = float(x1.replace('\n',''))
    send(sock, 'FREQ:STOP?')
    x2 = read(sock)
    x2 = float(x2.replace('\n',''))
    send(sock, 'TRAC?')
    y = read(sock)
    y = numpy.array(y.replace('\n','').split(','), dtype='float')
    x = numpy.linspace(x1, x2, len(y))
    return (x, y)

#==============================================================================

def main():
    """
    Main script
    """
    # Parse command line
    args = parse()
    # ip
    ip = str(args.ip)
    # port
    port = int(args.port)

    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
        sock.settimeout(10.0)
        sock.connect((ip, port))

        app = QtGui.QApplication([])

        win = pyqtgraph.GraphicsWindow(title='Basic FPC1000 viewer (%s:%i)'%(ip, port))

        pyqtgraph.setConfigOptions(antialias=True)

        global curve, ptr, p1
        p1 = win.addPlot(title="Spectrum")
        curve = p1.plot(pen='y')
        ptr = 0
        def update():
            global curve, ptr, p1
            (x_data, y_data) = get_spectrum(sock)
            curve.setData(x = x_data, y = y_data)
            if ptr == 0:
                p1.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
            ptr += 1
        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(500)

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    except:
        pass

        ## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    main()
