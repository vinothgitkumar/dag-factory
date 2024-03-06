'''
This script will delete all given Opensearch domains.

The Region and the target Opensearch Domain are in the input csv file.
    python3 opensearch_domain_deletion.py -p/--profile <sso profile name> -d/--dry-run True/False -f/--input-file <inputfile.csv> -a/--account-name <Account Name>

    python3 opensearch_domain_deletion.py -p cn-digital-non-prod -d False -f snapshots.csv -a cn-digital-non-prod

'''

import boto3
import csv
import argparse
import sys
import datetime

def os_domain_deletion(region,profile,domain_name,csv_writer):
    #Configure client session for given region
    sess = boto3.Session(profile_name=profile, region_name=region)
    os_client = sess.client('opensearch')
    try:
        domain_deletion_response = os_client.delete_domain(DomainName=domain_name)
        csv_writer.writerow([region,domain_name,'deleted',domain_deletion_response])
    except Exception as e:
        csv_writer.writerow([region,domain_name,'Error',e])

def main():
    a = argparse.ArgumentParser()
    a.add_argument('-p', '--profile', help='AWS SSO profile name to use', required=True)
    a.add_argument('-d', '--dry-run', help='Dry run mode', required=True)
    a.add_argument('-f', '--input-file', help='CSV file containing region and list of instances to terminate', required=True)
    a.add_argument('-a', '--account-name', help='account name will be used for output file name', required=True)

    #Parse the given commandline arguments
    args = a.parse_args()

    #Check the dry-run flag
    #args.dry_run = ast.literal_eval(args.dry_run)
    if (args.dry_run == "False" or args.dry_run == "false"):
        args.dry_run = False
    else:
        bool(args.dry_run)

    if args.dry_run == False:
        choice = input('Continue Opensearch Domain deletion? [Y/n] ')
        if not choice in {'y', 'Y'}:
            if choice in {'n', 'N'}:
                sys.exit()
            else:
                print("Provide valid input")
                sys.exit()
    elif (args.dry_run == 'True' or args.dry_run == 'true'):
        print("Disable DryRun Flag! The input should be False to disable dryrun.")
        sys.exit()
    else:
        print("Provide valid DryRun input: True [OR] False")
        sys.exit()
    
    #Check if the input file extension is .csv
    input_file = args.input_file
    if not input_file.endswith(".csv"):
        print("The input file is not a CSV file. Exiting the program.")
        sys.exit()

    profile = args.profile

    # Create a output csv file writer object
    account = args.account_name
    raw_timestamp = datetime.datetime.now()
    timestamp = raw_timestamp.strftime("%d%m%Y_%H%M")
    output_file = f"{account}-opensearch-domain-deletion-log-{timestamp}.csv"
    output_file = open(output_file, 'w')
    csv_writer = csv.writer(output_file, delimiter=',')

    # Write the header row
    csv_writer.writerow(['Region','Opensearch_Domain','Status','Response'])

    #Input CSV file reading and Column separation
    with open (input_file, "r") as myfile:
        csv_reader = csv.reader(myfile, delimiter=',')
        for row in csv_reader:
            region=row[0]
            domain_name=row[1]

            os_domain_deletion(region,profile,domain_name,csv_writer)

    #Close outfut file connection   
    output_file.close()

if __name__ == '__main__':
    main()
