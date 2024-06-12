from django.db import models
from account.models import Account
from urllib.parse import urlparse
import uuid
import re


class PolicySearch(models.Model):
	auto_increment_id   = models.AutoField(primary_key=True)
	created_at          = models.DateTimeField(auto_now_add=True)
	name                = models.CharField(verbose_name="Name", max_length=50)
	keywords 			= models.TextField(verbose_name="Keywords", default="", blank=True)  # Store keywords as a comma-separated string
	account 		    = models.ForeignKey(Account, on_delete=models.CASCADE)
	object_id           = models.CharField(verbose_name="object_id", max_length=50, blank=True)
	progress 	   		= models.IntegerField(default=0, blank=True)
	unique_thread_id 	= models.CharField(blank=True, null=True, max_length=100, default="")
	# no_indicators	 	= models.CharField(blank=True, null=True, max_length=50, default="False")
	


	def __str__(self):
		return self.name + " - " + self.account.email + " - " + str(self.created_at)
	

def parse_content(content):
    pattern = re.compile(r"INFORMATION:\s*(.*?)\s*SOURCE:\s*(.*?)\s*(?=INFORMATION:|$)", re.DOTALL)
    entries = []
    matches = pattern.findall(content)
    for info, source in matches:
        source_url = source.strip()
        parsed_url = urlparse(source_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}" if parsed_url.netloc else "Invalid URL or no source"
        entries.append({
            'information': info.strip(),
            'source': source_url,
            'domain': domain if domain != "Invalid URL or no source" else "No source available",
            'id': str(uuid.uuid4()) 
        })
    return entries