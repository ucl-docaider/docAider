from file2 import parse_content
import pandas as pd
from django.shortcuts import render, redirect
from collections import defaultdict
from django.templatetags.static import static
from file2 import PolicySearch

def manage_searches_view(request):
	if not request.user.is_authenticated:
		return redirect("policy_search:access_denied")
	
	context = {}
	if request.user.is_authenticated:
		policy_search_data = PolicySearch.objects.filter(account=request.user).order_by('-created_at')
		
		data_by_search = []

		for data in policy_search_data:
			grouped_by_country = defaultdict(list)
			grouped_by_policy = defaultdict(list)
			if data.object_id:
				file_path_excel = str(request.user.id) + "/policy_search/finished_files/" + data.object_id 
				file = static(file_path_excel)
				df = pd.read_csv(file)
				for _, row in df.iterrows():
					entries = parse_content(row['Content'])
					grouped_by_country[row['Country']].append({'policy': row['Policy'], 'entries': entries})
					grouped_by_policy[row['Policy']].append({'country': row['Country'], 'entries': entries})
				
				data_by_search.append({
					'search_name': data.name,
					'search_id': data.auto_increment_id,
					'grouped_data_by_policy': dict(grouped_by_policy),
					'grouped_data_by_country': dict(grouped_by_country)
				})

		context['data_by_search'] = data_by_search
	
	return render(request, "policy_search/manage_searches.html", context)