#!/usr/bin/env python3
# @ih3bski
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
import uuid
from loguru import logger
import sys
import argparse
import fire
from datetime import datetime, date
import csv
from sqlalchemy import cast, Date

app = Flask(__name__)

# Change the default db path
dbname = "bb_record"
dbpath = "/tmp"
result_save_dir = "/tmp"

# SQLAlchemy config/Disable warnings for a clean output $_$
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}/{dbname}.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
stats = logger.level("STATS", no=38, color="<yellow>", icon="📈")
Counter = 0
results = 0

# Model -> T.B changed
class Target(db.Model):
    __tablename__ = 'Target'
    id = db.Column(db.Text, primary_key=True)
    subdomain = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.today().replace(microsecond=0))

    def __init__(self,subdomain,id):
    	self.id = id
    	self.subdomain = subdomain

db.create_all()

def save(subdomain):
	"""
	Save subdomains to databse
	"""
	global Counter
	if db.session.query(Target.id).filter_by(subdomain=subdomain).scalar() is None :
		db.session.add(Target(subdomain,str(uuid.uuid4())))
		db.session.commit()
		Counter += 1
		logger.log('INFO',f'[+] {subdomain} added to database')
	else:
		logger.log('ERROR',f'[-] {subdomain} already exists')

def searchByDomain(subdomain):
	return db.session.query(Target).filter(Target.subdomain.like(f"%{subdomain}%")).all()

def search(subdomain):
	"""
	Search a list of subdomains
	"""
	sub = searchByDomain(subdomain)
	if sub :
		results = sub
		for row in sub:
			logger.log('INFO',row.subdomain)
		logger.log("STATS", f'We have found {len(sub)} subdomains ! Happy Hacking $_$')
	else:
		logger.log('WARNING',f'[-] {subdomain} NOT FOUND.')

def remove(subdomain):
	"""
	Remove One subdomain from the database
	"""
	if Target.query.filter(Target.subdomain == subdomain).delete():
		db.session.commit()
		logger.log("INFO",f'[+] {subdomain} was deleted successfully.')
	else:
		logger.log("ERROR",f'[+] Failed while trying to remove {subdomain} check your request!')

def removeall(subdomain):
	"""
	Remove all domains related like subdomains
	"""
	Target.query.filter(Target.subdomain.like(f"%{subdomain}%")).delete(synchronize_session='fetch')
	db.session.commit()
	print("deleted",sub)

def new():
	"""
	Show the new added subdomains, filter by today date.
	"""
	sub = db.session.query(Target).filter(func.date(Target.created_date) == date.today()).all()
	if sub.count :
		for row in sub:
			logger.log("INFO",f"{row.subdomain}")
	else:
		logger.log('WARNING',f'[-] No record added for today')

def all():
	"""
	Get all database results
	"""
	sub = db.session.query(Target).all()
	if sub :
		for row in sub:
			logger.log('INFO',f"{row.created_date} {row.subdomain}")
		logger.log("STATS", f'{len(sub)} bulks! $_$')
	else:
		logger.log('WARNING',f'[-] Database is empty')

def wipe():
	"""
	Delete all record in the database
	"""
	db.session.query(Target).delete()
	db.session.commit()

def exportToCSV(subdomain,sub,file_name):
	"""
	Export subdomains as csv format
	"""
	try:
		with open(file_name,"w") as file:
			fnames = ['subdomain', 'saved_date']
			writer = csv.DictWriter(file, fieldnames=fnames)
			writer.writeheader()
			for _ in sub:
				writer.writerow({'subdomain' : _.subdomain, 'saved_date': _.created_date})
			print(f'[+] {len(sub)} results of {subdomain} exported successfully.\n[+] Path {result_save_dir}/{subdomain}_{datetime.now().date()}.csv')
	except IOError as error:
		logger.log("ERROR","[+] Fails to open or create file! Please check your permissions")

def exportToTXT(subdomain,sub,file_name):
	"""
	Export subdomains as txt format 
	"""
	try:
		f = open(file_name, 'w')
		for _ in sub:
			f.write(f'{_.subdomain}\n')
		print(f'[+] {len(sub)} results of {subdomain} exported successfully.\n[+] Path {result_save_dir}/{subdomain}_{datetime.now().date()}.txt')
	except IOError as error:
		logger.log("ERROR","[+] Fails to open or create file! Please check your permissions")

def export(subdomain,format="txt"):
	"""
	Export results as txt,csv format
	default_dir/domain.com_date.{txt,csv}
	"""
	rows = searchByDomain(subdomain)
	if rows:
		if format == "csv":
			exportToCSV(subdomain,rows,f'{result_save_dir}/{subdomain}_{datetime.now().date()}.csv')	
		elif format == "txt" :
			exportToTXT(subdomain,rows,f'{result_save_dir}/{subdomain}_{datetime.now().date()}.txt')
		else:
			logger.log("ERROR","This format is not supported yet !")
	else:
		logger.log("ERROR","[+] Cannot export the file, please check your query :)")

if __name__ == '__main__':
	# use stdin if it's full                                                        
	if not sys.stdin.isatty():
	    for subdomains in sys.stdin:
	    	save(subdomains.strip())
	    logger.log("STATS", f'{Counter} Bulk added ^_^ !')
	# read subdomain as argument                                            
	else:
		fire.Fire()
