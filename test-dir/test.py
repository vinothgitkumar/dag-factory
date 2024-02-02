import argparse
import sys
from time import sleep

import dns.resolver
import boto3



def is_global_dns_delegated_set(ns_records):
    # from: https://github.com/CondeNast/global-dns
    return ns_records == set([
        'ns-1935.awsdns-49.co.uk.',
        'ns-28.awsdns-03.com.',
        'ns-836.awsdns-40.net.',
        'ns-1116.awsdns-11.org.'
    ])


def get_hosted_zone_records(boto_client, hosted_zone_id, zone_name, record_type):
    '''Find NS records on apex'''

    print('Processing: ', zone_name)
    records = boto_client.get_paginator(
        'list_resource_record_sets'
    )

    paginator = records.paginate(HostedZoneId=hosted_zone_id)
    ns_records = set()

    backoff = 10

    while True:
        try:
            for record_set in paginator:
                for record in record_set['ResourceRecordSets']:
                    if record['Type'] == record_type and record['Name'] == zone_name:
                        # apex NS only
                        vals = [x['Value'] for x in record['ResourceRecords']]
                        for x in vals:
                            ns_records.add(x)
        except boto_client.exceptions.ClientError:
            print('Backoff: {}s'.format(backoff))
            sleep(backoff)
            backoff *= 2
        else:
            break

    print('Found {} apex NS records'.format(len(ns_records)))
    return ns_records


def get_public_zone_ns(zone_name):
    '''Query public dns to find NS servers'''
    ns_records = set()

    r = dns.resolver.Resolver()
    r.nameservers = ['1.1.1.1', '1.0.0.1']

    try:
        answers = r.resolve(zone_name, 'NS')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
        # no answer
        pass
    else:
        for a in answers:
            ns_records.add(a.to_text())

    return ns_records


def trawl_zones(boto_client):
    '''Trawl zones in an account'''
    zones = boto_client.get_paginator('list_hosted_zones')
    zone_paginator = zones.paginate()

    r53_zone_to_ns_list = {}
    public_zone_to_ns_list = {}

    for page in zone_paginator:
        for zone in page['HostedZones']:
            # only look at public zones
            if not zone['Config']['PrivateZone']:

                r53_zone_to_ns_list[zone['Name']] = get_hosted_zone_records(
                    boto_client,
                    zone['Id'],
                    zone['Name'],
                    'NS'
                )

                public_zone_to_ns_list[zone['Name']] = get_public_zone_ns(
                    zone['Name']
                )

                sleep(0.25)


    if not set(r53_zone_to_ns_list.keys()) == set(public_zone_to_ns_list.keys()):
        print('Lengths did not match, exit')
        sys.exit()

    print('Analysed {} zones'.format(len(r53_zone_to_ns_list)))

    actives = []
    inactives = []
    global_dns = []

    for zone in r53_zone_to_ns_list:
        print(zone)
        print('-' * len(zone))

        if r53_zone_to_ns_list[zone] == public_zone_to_ns_list[zone]:
            print('Active: {}'.format(zone))
            actives.append(zone)
        else:
            print('Inactive: {}'.format(zone))
            print('R53: {}'.format(r53_zone_to_ns_list[zone]))
            print('Public: {}'.format(public_zone_to_ns_list[zone]))
            inactives.append(zone)

        if is_global_dns_delegated_set(public_zone_to_ns_list[zone]):
            print('> Additional: On Global DNS!')
            global_dns.append(zone)

        print('')

    print('--------')
    print('')
    print('Summary')
    print('Active: {}'.format(len(actives)))
    print('Inactive: {}'.format(len(inactives)))
    print(' of which on Global DNS: {}'.format(len(global_dns)))

    print('Active:')
    for x in actives:
        print('   ', x)

    print('Inactive:')
    for x in inactives:
        print('   ', x)

    print('NS on Global DNS:')
    for x in global_dns:
        print('   ', x)


def get_nameservers_for_zone(zone_name):
    pass


def delete_zone(): pass
def delete_zones(): pass


if __name__ == '__main__':

    a = argparse.ArgumentParser()
    a.add_argument('-p', '--profile', required=True)


    a.add_argument('-d', '--delete', required=False, action='store_true')
    a.add_argument('-a', '--audit', required=False, action='store_true')

    a.add_argument('-z', '--zone', required=False)
    a.add_argument('-i', '--input', required=False)

    args = a.parse_args()

    s = boto3.Session(profile_name=args.profile)
    r53 = s.client('route53')

    if args.audit:
        # we're in audit mode
        trawl_zones(r53)
    elif args.input and not args.zone:
        # delete zones from input
        delete_zones(r53, args.input)
    elif args.input and args.zone:
        # delete zone
        delete_zone(r53, args.zone)
    else:
        print('Nothing to do. See --help.')
        sys.exit(1)
