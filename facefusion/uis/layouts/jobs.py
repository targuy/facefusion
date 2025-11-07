import os
import gradio

from facefusion import state_manager
from facefusion.uis.components import about, job_list, job_list_options


def pre_check() -> bool:
	return True


def render() -> gradio.Blocks:
	with gradio.Blocks() as layout:
		with gradio.Row():
			with gradio.Column(scale = 4):
				with gradio.Blocks():
					about.render()
				with gradio.Blocks():
					job_list_options.render()
			with gradio.Column(scale = 11):
				with gradio.Blocks():
					job_list.render()
	return layout


def listen() -> None:
	job_list_options.listen()
	job_list.listen()


def run(ui : gradio.Blocks) -> None:
	# Check if running in GitHub Codespaces
	is_codespace = os.environ.get('CODESPACES') == 'true'
	
	if is_codespace:
		# Configuration pour GitHub Codespaces
		print("🚀 Lancement de FaceFusion dans GitHub Codespaces...")
		print("🌐 Création d'un lien public Gradio pour l'accès...")
		ui.launch(
			favicon_path = 'facefusion.ico', 
			inbrowser = False,  # Désactiver l'ouverture automatique du navigateur
			server_name = '0.0.0.0',  # Écouter sur toutes les interfaces
			server_port = 7860,  # Port fixe pour le forwarding
			share = True,  # Créer un lien public Gradio
			show_api = False,  # Masquer la documentation API
			quiet = False  # Afficher les messages de lancement
		)
	else:
		# Configuration normale
		ui.launch(favicon_path = 'facefusion.ico', inbrowser = state_manager.get_item('open_browser'))
