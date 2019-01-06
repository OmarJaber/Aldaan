from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on transactions against this Healthcare Practitioner.'),
		'fieldname': 'practitioner',
		'transactions': [
			{
				'label': _('Appointments and Patient Encounters'),
				'items': ['Patient Appointment', 'Patient Encounter']
			},
			{
				'label': _('Lab Tests'),
 				'items': ['Lab Test']
			}
		]
	}
