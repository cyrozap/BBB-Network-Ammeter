#!/usr/bin/env python
#
# BBB-Network-Ammeter
#
# Copyright (c) 2016, Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from datetime import datetime

from lxml import etree
from flask import Flask, Response
from Adafruit_BBIO import ADC

app = Flask(__name__)

def get_current():
    voltage = get_adc_voltage()
    current = 109.2 * voltage + 5.3688
    return current

def get_adc_voltage():
    # Read a value from the ADC
    value = ADC.read("P9_39") # AIN0

    # Convert the number to a voltage
    voltage = value * 1.8

    return voltage

@app.route("/sample")
def sample():
    voltage = get_adc_voltage()
    return Response("{:.03f} V".format(voltage))

@app.route("/probe")
def probe():
    '''Generate a response for probe requests'''
    mtconnect_schema = "urn:mtconnect.org:MTConnectDevices:1.3"
    schema_url = "http://www.mtconnect.org/schemas/MTConnectDevices_1.3.xsd"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    MTConnectDevices = etree.Element("MTConnectDevices",
        nsmap={
            None: mtconnect_schema,
            "xsi": xsi,
            "m": mtconnect_schema,
        }
    )
    MTConnectDevices.attrib["{{{pre}}}schemaLocation".format(pre=xsi)] = \
        "{schema} {schema_url}".format(schema=mtconnect_schema, schema_url=schema_url)

    creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    Header = etree.SubElement(MTConnectDevices, "Header",
        creationTime=creation_time,
        instanceId="0",
        sender="mtcagent",
        bufferSize="0",
        version="0.1",
        assetCount="1",
    )

    Devices = etree.SubElement(MTConnectDevices, "Devices")
    Device = etree.SubElement(Devices, "Device",
        id="dev",
        iso841Class="6",
        name="currentSensor",
        sampleInterval="10",
        uuid="0",
    )
    Description = etree.SubElement(Device, "Description",
        manufacturer="RPI MILL",
    )
    DataItems_0 = etree.SubElement(Device, "DataItems")
    DataItem_0 = etree.SubElement(DataItems_0, "DataItem",
        category="EVENT",
        id="avail",
        type="MACHINE_ON",
    )
    Components_0 = etree.SubElement(Device, "Components")
    Axes = etree.SubElement(Components_0, "Axes", id="ax", name="Axes")
    Components_1 = etree.SubElement(Axes, "Components")
    Linear = etree.SubElement(Components_1, "Linear", id="x1", name="X")
    DataItems_1 = etree.SubElement(Linear, "DataItems")
    DataItem_1 = etree.SubElement(DataItems_1, "DataItem",
        category="SAMPLE",
        id="current1",
        name="current1",
        nativeUnits="AMPERE",
        subType="ACTUAL",
        type="CURRENT",
        units="AMPERE",
    )

    response = etree.tostring(MTConnectDevices,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'
    )
    return Response(response, mimetype='text/xml')

@app.route("/current")
def current():
    mtconnect_schema = "urn:mtconnect.org:MTConnectStreams:1.3"
    schema_url = "http://www.mtconnect.org/schemas/MTConnectStreams_1.3.xsd"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    MTConnectStreams = etree.Element("MTConnectStreams",
        nsmap={
            None: mtconnect_schema,
            "xsi": xsi,
            "m": mtconnect_schema,
        }
    )
    MTConnectStreams.attrib["{{{pre}}}schemaLocation".format(pre=xsi)] = \
        "{schema} {schema_url}".format(schema=mtconnect_schema, schema_url=schema_url)

    creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    Header = etree.SubElement(MTConnectStreams, "Header",
        creationTime=creation_time,
        instanceId="0",
        sender="mtcagent",
        bufferSize="0",
        version="0.1",
        assetCount="1",
    )

    Streams = etree.SubElement(MTConnectStreams, "Streams")
    DeviceStream = etree.SubElement(Streams, "DeviceStream",
        name="VMC-3Axis",
        uuid="0",
    )
    ComponentStream = etree.SubElement(DeviceStream, "ComponentStream",
        component="Rotary",
        name="C",
        componentId="c1",
    )
    Samples = etree.SubElement(ComponentStream, "Samples")
    Current = etree.SubElement(Samples, "Current",
        dataItemId="c2",
        timestamp=datetime.utcnow().isoformat(),
        name="Scurrent",
        sequence="8403169415",
        subType="ACTUAL",
    )
    Current.text = "{current:.03f}".format(current=get_current())

    Events = etree.SubElement(ComponentStream, "Events")
    MachineMode = etree.SubElement(Events, "MachineMode",
        dataItemId="machineMode",
        timestamp=datetime.utcnow().isoformat(),
        name="Cmode",
        sequence="18"
    )
    MachineMode.text = "ON"

    response = etree.tostring(MTConnectStreams,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'
    )
    return Response(response, mimetype='text/xml')


if __name__ == "__main__":
    ADC.setup()
    app.run(host='0.0.0.0', debug=False)
