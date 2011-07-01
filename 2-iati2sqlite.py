from lxml import etree
from pprint import pprint
import csv
import sqlalchemy
import os
from sqlalchemy import create_engine
engine = create_engine('sqlite:///iatidata_new.sqlite', echo=False)

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, UnicodeText, Date, Float
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
Session = sessionmaker()
session = Session()


Base = declarative_base()

Base.metadata.bind = engine
class Activity(Base):
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    package_id = Column(UnicodeText)
    source_file = Column(UnicodeText)
    activity_lang = Column(UnicodeText)
    default_currency = Column(UnicodeText)
    hierarchy = Column(UnicodeText)
    last_updated = Column(UnicodeText)
    reporting_org = Column(UnicodeText)
    reporting_org_ref = Column(UnicodeText)
    reporting_org_type = Column(UnicodeText)
    funding_org = Column(UnicodeText)
    funding_org_ref = Column(UnicodeText)
    funding_org_type = Column(UnicodeText)
    extending_org = Column(UnicodeText)
    extending_org_ref = Column(UnicodeText)
    extending_org_type = Column(UnicodeText)
    implementing_org = Column(UnicodeText)
    implementing_org_ref = Column(UnicodeText)
    implementing_org_type = Column(UnicodeText)
    recipient_region = Column(UnicodeText)
    recipient_region_code = Column(UnicodeText)
    recipient_country = Column(UnicodeText)
    recipient_country_code = Column(UnicodeText)
    collaboration_type = Column(UnicodeText)
    collaboration_type_code = Column(UnicodeText)
    flow_type = Column(UnicodeText)
    flow_type_code = Column(UnicodeText)
    aid_type = Column(UnicodeText)
    aid_type_code = Column(UnicodeText)
    finance_type = Column(UnicodeText)
    finance_type_code = Column(UnicodeText)
    iati_identifier = Column(UnicodeText)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    date_start_actual = Column(UnicodeText)
    date_start_planned = Column(UnicodeText)
    date_end_actual = Column(UnicodeText)
    date_end_planned = Column(UnicodeText)
    status_code = Column(UnicodeText)
    status = Column(UnicodeText)
    contact_organisation = Column(UnicodeText)
    contact_telephone = Column(UnicodeText)
    contact_email = Column(UnicodeText)
    contact_mailing_address = Column(UnicodeText)
    tied_status = Column(UnicodeText)
    tied_status_code = Column(UnicodeText)
    activity_website = Column(UnicodeText)
    #countryregion_id = Column(

class Transaction(Base):
    __tablename__ = 'atransaction'
    id = Column(Integer, primary_key=True)
    activity_id = Column(UnicodeText)
    value = Column(Float)
    iati_identifier = Column(UnicodeText)
    value_date = Column(UnicodeText)
    value_currency = Column(UnicodeText)
    transaction_type = Column(UnicodeText)
    transaction_type_code = Column(UnicodeText)
    provider_org = Column(UnicodeText)
    provider_org_ref = Column(UnicodeText)
    provider_org_type = Column(UnicodeText)
    receiver_org = Column(UnicodeText)
    receiver_org_ref = Column(UnicodeText)
    receiver_org_type = Column(UnicodeText)
    description = Column(UnicodeText)
    transaction_date = Column(UnicodeText)
    transaction_date_iso = Column(Date)
    flow_type = Column(UnicodeText)
    flow_type_code = Column(UnicodeText)
    aid_type = Column(UnicodeText)
    aid_type_code = Column(UnicodeText)
    finance_type = Column(UnicodeText)
    finance_type_code = Column(UnicodeText)
    tied_status_code = Column(UnicodeText)
    disbursement_channel_code = Column(UnicodeText)

# Put everything into sectors table, and link back to activity. This will create a new unique sector per activity, which is OK for then importing back into OS but obviously you would probably want an activities_sectors table to handle a relationship between unique activities and unique sectors.
 
class Sector(Base):
    __tablename__ = 'sector'
    id = Column(Integer, primary_key=True)   
    activity_iati_identifier = Column(UnicodeText)
    name = Column(UnicodeText)
    vocabulary = Column(UnicodeText)
    code = Column(UnicodeText)
    percentage = Column(Integer)

class RelatedActivity(Base):
    __tablename__ = 'relatedactivity'
    id = Column(Integer, primary_key=True)
    activity_id = Column(UnicodeText)
    reltext = Column(UnicodeText)
    relref = Column(UnicodeText)
    reltype = Column(UnicodeText)

Base.metadata.create_all()

def nodecpy(out, node, name, attrs={}, convert=unicode):
    if node is None:
        return
    if node.text:
        out[name] = convert(node.text)
    for k, v in attrs.items():
        out[name + '_' + v] = node.get(k)

def parse_tx(tx):
    out = {}
    value = tx.find('value')
    if value is not None:
        out['value_date'] = value.get('value-date')
        out['value_currency'] = value.get('currency')
        out['value'] = float(value.text)
    if tx.findtext('description'):
        out['description'] = tx.findtext('description')
    nodecpy(out, tx.find('activity-type'),
            'transaction_type', {'code': 'code'})
    nodecpy(out, tx.find('transaction-type'),
            'transaction_type', {'code': 'code'})
    nodecpy(out, tx.find('flow-type'),
            'flow_type', {'code': 'code'})
    nodecpy(out, tx.find('finance-type'),
            'finance_type', {'code': 'code'})
    nodecpy(out, tx.find('tied-status'),
            'tied_status', {'code': 'code'})
    nodecpy(out, tx.find('aid-type'),
            'aid_type', {})
    get_date(out, tx, 'transaction-date', 'transaction_date_iso')
    if tx.findtext('transaction-date'):
        out['transaction_date'] = tx.findtext('transaction-date')
    nodecpy(out, tx.find('disembursement-channel'),
            'disembursement_channel', {'code': 'code'})
    nodecpy(out, tx.find('provider-org'),
            'provider_org', {'ref': 'ref'})
    nodecpy(out, tx.find('receiver-org'),
            'receiver_org', {'ref': 'ref'})
    return out

def get_date(out, node, name, key):
    de = node.find('activity-date[@type="%s"]' % name)
    if de is not None:
        out[key] = de.get('iso-date')

def parse_activity(activity, out):
    out['default_currency'] = activity.get("default-currency")
    nodecpy(out, activity.find('reporting-org'),
            'reporting_org', {'ref': 'ref', 
                              'type': 'type'})
    
    out['iati_identifier'] = activity.findtext('iati-identifier')
    if activity.findtext('activity-website'):
        out['activity_website'] = activity.findtext('activity-website')
    out['title'] = activity.findtext('title')
    if activity.findtext('description'):
        out['description'] = activity.findtext('description')
    if activity.findtext('recipient-region'):
        out['recipient_region'] = activity.findtext('recipient-region')
    nodecpy(out, activity.find('recipient-country'),
            'recipient_country', {'code': 'code'})
    nodecpy(out, activity.find('collaboration_type'),
            'collaboration_type', {'code': 'code'})
    nodecpy(out, activity.find('default-flow-type'),
            'flow_type', {'code': 'code'})
    nodecpy(out, activity.find('default-finance-type'),
            'finance_type', {'code': 'code'})
    nodecpy(out, activity.find('default-tied-status'),
            'tied_status', {'code': 'code'})
    nodecpy(out, activity.find('default-aid-type'),
            'aid_type', {})
    nodecpy(out, activity.find('activity-status'),
            'status', {})
    nodecpy(out, activity.find('legacy-data'),
            'legacy', {'name': 'name', 'value': 'value'})
    
    nodecpy(out, activity.find('participating-org[@role="Funding"]'),
            'funding_org', {'ref': 'ref', 'type': 'type'})
    nodecpy(out, activity.find('participating-org[@role="Extending"]'),
            'extending_org', {'ref': 'ref', 'type': 'type'})
    nodecpy(out, activity.find('participating-org[@role="Implementing"]'),
            'implementing_org', {'ref': 'ref', 'type': 'type'})
    
    #get_date(out, activity, 'start-planned', 'start_planned')
    #get_date(out, activity, 'start-actual', 'start_actual')
    #get_date(out, activity, 'end-planned', 'end_planned')
    #get_date(out, activity, 'end-actual', 'end_actual')
       
    for date in activity.findall('activity-date'):
        try:
            # for some (WB) projects, the date is not set even though the tag exists...
            if (date.text is not None):
                temp = {}
                nodecpy(temp, date,
                    'date',
                    {'type': 'type', 'iso-date': 'iso-date'})
                 
                datetype = temp['date_type']
                
                if ((datetype == 'start-actual') and (temp['date'])):
                    d = (temp['date'])
                    out['date_start_actual'] = d
                if ((datetype == 'start-planned') and (temp['date'])):
                    d = (temp['date'])
                    out['date_start_planned'] = d
                if ((datetype == 'end-actual') and (temp['date'])):
                    d = (temp['date'])
                    out['date_end_actual'] = d
                if ((datetype == 'end-planned') and (temp['date'])):
                    d = (temp['date'])
                    out['date_end_planned'] = d
            else:
                print "No date!!"
           
        except ValueError:
            pass
    
    nodecpy(out, activity.find('contact-info/organisation'),
            'contact_organisation', {})
    nodecpy(out, activity.find('contact-info/mailing-address'),
            'contact_mailing_address', {})
    nodecpy(out, activity.find('contact-info/telephone'),
            'contact_telephone', {})
    nodecpy(out, activity.find('contact-info/email'),
            'contact_email', {})
    
    # SLIGHTLY HACKY:
    """snd_level = 0
    for policy_marker in activity.findall('policy-marker'):
        try:
            sign = int(policy_marker.get('significance'))
            if sign == 0:
                continue
            if sign == 2:
                snd_level += 1
            nodecpy(out, policy_marker,
                'policy_marker_' + policy_marker.get('code'), 
                {'vocabulary': 'vocabulary', 'significance': 'significance'})
        except ValueError:
            pass
    """
    for sector in activity.findall('sector'):
        try:
            temp = {}
            nodecpy(temp, sector,
                'sector',
                {'vocabulary': 'vocabulary', 'percentage': 'percentage', 'code': 'code'})
             
            vocab = temp['sector_vocabulary'] if temp['sector_vocabulary'] else 'DAC'
            activityiatiid = activity.findtext('iati-identifier')
            getpercentage = temp['sector_percentage']
            percentage = 0
            # if getpercentage doesn't exist, or it's blank, or it's None, do this:
            if (not(getpercentage) or (getpercentage == '') or (getpercentage is None)):
                percentage = 100
            else:
            # if getpercentage exists, it's not blank, and it's not none
                percentage = getpercentage
                
            tsector = {
                'activity_iati_identifier': activityiatiid,
                'name': temp['sector'],
                'code': temp['sector_code'],
                'percentage': int(percentage),
                'vocabulary': vocab
            }
            missingfields(sector, Sector)
            s = Sector(**tsector)
            session.add(s)
        except ValueError:
            pass
            
    for ra in activity.findall('related-activity'):
        try:
            ratemp = {}
            nodecpy(ratemp, ra,
                'related_activity',
                {'type': 'type', 'ref': 'ref'})
            activityiatiid = activity.findtext('iati-identifier')
            related_activity = {
                'activity_id': activityiatiid,
                'reltext': ratemp['related_activity'],
                'relref': ratemp['related_activity_ref'],
                'reltype': ratemp['related_activity_type']                    
            }
            missingfields(related_activity, RelatedActivity)
            rela = RelatedActivity(**related_activity)
            session.add(rela)
        except ValueError:
            pass
             
    for tx in activity.findall("transaction"):
        transaction = parse_tx(tx)
        transaction['iati_identifier'] = out['iati_identifier']
        missingfields(transaction, Transaction)
        t = Transaction(**transaction)
        session.add(t)
    missingfields(out, Activity)
    x = Activity(**out) 
    session.add(x)
    session.commit()
    return (out)

def missingfields(dict_, obj):
    missing = [ k for k in dict_ if k not in obj.__table__.c.keys() ]
    if missing:
        print "XXXX ", obj.__name__, missing
    for m in missing:
        del dict_[m]

def load_file(file_name, context=None):
    doc = etree.parse(file_name)
    if context is None:
        context = {}
    context['source_file'] = file_name
    print "Parsing ", file_name
    for activity in doc.findall("iati-activity"):
        out = parse_activity(activity, context.copy())


# replace load_registry with load_package (run iatidownload.py to create packages in /packages first)
def load_package():
    path = 'packages/'
    listing = os.listdir(path)
    for infile in listing:
        try:
            load_file('packages/' + infile)
        except Exception, e:
            print 'Failed:', e
            
# previously: load direct from registry. now downlaod packages first, then iterate with load_package
def load_registry(url='http://iatiregistry.org/api'):
    import ckanclient
    registry = ckanclient.CkanClient(base_location=url)
    startnow = False
    for pkg_name in registry.package_register_get():
        # testing - get one package only
        if (pkg_name == 'wb-zw'):
            pkg = registry.package_entity_get(pkg_name)
            for resource in pkg.get('resources', []):
                print resource.get('url')
                try:
                    load_file(resource.get('url'))
                except Exception, e:
                    print "Failed:", e

def write_csv(transactions, filename='iati.csv'):
    fh = open(filename, 'w')
    keys = []
    for transaction in transactions:
        keys.extend(transaction.keys())
    writer = csv.DictWriter(fh, fieldnames=list(set(keys)))
    writer.writerow(dict([(k,k) for k in keys]))
    for transaction in transactions:
        row = dict([(k, unicode(v).encode('utf-8')) for (k, v) in transaction.items() if
            v is not None])
        writer.writerow(row)
    fh.close()

if __name__ == '__main__':
    import sys
    #transactions = load_file(sys.argv[1])
    load_package()
    print session.query(Activity).count()
    print session.query(Transaction).count()