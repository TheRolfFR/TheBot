# Écrire la clé de l'entrée en CamelCase et l'URL vers le flux MP3 128kbps
#pour le francophone ce site est simple http://fluxradios.blogspot.com/

from .radiodescription import RadioDescription

radioList = [
  RadioDescription(display_name='Autoroute Info', url='http://media.autorouteinfo.fr:8000/direct_nord.mp3', aliases=['AutorouteInfo', 'ai']),
  RadioDescription(display_name='BFM Business', url='http://chai5she.cdn.dvmr.fr/bfmbusiness', aliases=['BFMBusiness', 'bfmb']),
  RadioDescription(display_name='Classic FM', url='http://media-ice.musicradio.com/ClassicFMMP3', aliases=['ClassicFM', 'cfm']),
  RadioDescription(display_name='France Culture', url='http://icecast.radiofrance.fr/franceculture-midfi.mp3', aliases=['FranceCulture', 'fc']),
  RadioDescription(display_name='France Bleu Belfort Montbeliard', url='http://icecast.radiofrance.fr/fbbelfort-midfi.mp3', aliases=['FBBelfortMontbeliard', 'fbbm']),
  RadioDescription(display_name='France Bleu Besancon', url='http://icecast.radiofrance.fr/fbbesancon-midfi.mp3', aliases=['FBBesancon', 'fbb']),
  RadioDescription(display_name='Nostalgie', url='http://185.52.127.160/fr/30601/mp3_128.mp3', aliases=['Nostalgie', 'nosta']),
  RadioDescription(display_name='Nova', url='http://novazz.ice.infomaniak.ch/novazz-128.mp3', aliases=['Nova']),
  RadioDescription(display_name='NRJ', url='http://cdn.nrjaudio.fm/audio1/fr/30001/mp3_128.mp3', aliases=['NRJ']),
  RadioDescription(display_name='OUIFM', url='http://stream.ouifm.fr/ouifm-high.mp3', aliases=['OUIFM']),
  RadioDescription(display_name='RadioBeur', url='https://beurfm.ice.infomaniak.ch/beurfm-high.mp3', aliases=['RadioBeur']),
  RadioDescription(display_name='Radio Classique', url='http://radioclassique.ice.infomaniak.ch/radioclassique-high.mp3', aliases=['RadioClassique', 'rc']),
  RadioDescription(display_name='Radio Swiss Jazz', url='http://stream.srg-ssr.ch/m/rsj/mp3_128', aliases=['RadioSwissJazz', 'rsj']),
  RadioDescription(display_name='Radio Regenbogen', url='https://streams.regenbogen.de/rr-mannheim-128-mp3', aliases=['RadioRegenbogen', 'rr']),
  RadioDescription(display_name='Rire Et Chansons', url='http://185.52.127.168/fr/30401/mp3_128.mp3', aliases=['RireEtChansons', 'rec']),
  RadioDescription(display_name='RTL', url='http://streaming.radio.rtl.fr/rtl-1-44-128', aliases=['RTL']),
  RadioDescription(display_name='RTL2', url='http://streaming.radio.rtl2.fr/rtl2-1-44-128', aliases=['RTL2']),
  RadioDescription(display_name='Skyrock', url='http://icecast.skyrock.net/s/natio_mp3_128k', aliases=['Skyrock', 's'])
]
