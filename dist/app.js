'use strict';
const form=document.querySelector('#profile');
const output=document.querySelector('#prompt-text');
const status=document.querySelector('#status');
function makePrompt(values={}){
 const value=(name,fallback)=>String(values[name]||'').trim()||fallback;
 return `Aide-moi à réduire les émissions de mes déplacements vers l’université, en respectant mes contraintes.

MA SITUATION
- Départ : ${value('origin','[quartier ou gare proche — inutile de donner mon domicile exact]')}.
- Destination : bâtiment IBGBI, 23 boulevard de France, Évry-Courcouronnes. Vérifie le point d’arrivée et l’accès à l’entrée.
- Jour : ${value('day','[à préciser]')}. Heure d’arrivée souhaitée : ${value('arrival','[à préciser]')}.
- Mode habituel : ${value('mode','[à préciser]')}. Durée habituelle porte-à-porte : ${value('duration','[à préciser]')}.
- Jours sur place par semaine : ${value('days','[à préciser]')}.
- Abonnements et équipements : ${value('equipment','[Navigo, vélo, voiture…]')}.
- Budget supplémentaire maximal : ${value('budget','[à préciser]')} €/mois.
- Surtemps maximal accepté : ${value('extra','[à préciser]')} minutes par aller.
- Marche, vélo, météo, mobilité et autres contraintes : ${value('constraints','[à préciser]')}.

QUATRE DEGRÉS DE CHANGEMENT
Propose jusqu’à quatre alternatives, du changement le plus léger au plus important :
1. Une petite adaptation de mon trajet habituel : horaires, correspondance ou étape finale.
2. Une solution occasionnelle : par exemple du covoiturage certains jours si les horaires coïncident.
3. Une combinaison de modes : par exemple vélo + RER ou marche + transports.
4. Une solution plus ambitieuse, uniquement si elle est réaliste pour ma distance et mes capacités.
Ne force pas quatre solutions si certaines sont irréalisables. Si une information essentielle manque, pose-moi des questions avant de chiffrer.

COMPARAISON DEMANDÉE
Présente mon trajet habituel puis les alternatives dans un tableau. Pour chacune, précise :
- Les étapes, les lignes et les modes empruntés.
- Le temps porte-à-porte : marche, prise/restitution d’un vélo, attente, correspondances et éventuel détour inclus.
- Le coût supplémentaire par rapport à ma situation : distingue abonnement déjà détenu, nouvel abonnement et frais variables. Donne les coûts par aller et par mois avec les hypothèses.
- Les émissions estimées en CO2e par personne et par aller, puis l’écart avec mon trajet habituel. Ajoute une fourchette si les hypothèses sont incertaines.
- Les contreparties : marche, effort, changements, pluie, disponibilité et organisation.
- Le respect ou le dépassement de mes limites, et une solution de repli sous la pluie.

SOURCES ET FIABILITÉ
Recherche des sources officielles actuelles pour les itinéraires, les tarifs et les aides. Cite les liens et la date de consultation. Ne prétends pas avoir vérifié une information si tu n’as pas accès au Web ou aux données nécessaires.
Vérifie notamment les dispositifs de covoiturage liés au Navigo et les aides à l’achat d’un vélo selon mon âge et ma résidence ; ne suppose pas que j’y suis éligible.
N’invente ni horaire, ni station vélo, ni disponibilité, ni aide, ni chiffre. Distingue les données vérifiées, les estimations et les informations à confirmer. Ne transforme pas un horaire prévu en garantie de ponctualité.

CALCUL DU CO2e
Indique les distances, les facteurs par voyageur-kilomètre, leur source et leur périmètre. Calcule la somme des émissions des segments ; ne divise pas une seconde fois un facteur déjà exprimé par personne.
N’applique pas automatiquement le facteur d’un vélo personnel à un vélo partagé : leur fabrication, maintenance et redistribution peuvent différer.
Pour le covoiturage, indique l’occupation, le détour et les trajets réellement remplacés. Remplacer un trajet en RER ou à pied par une voiture partagée n’est pas forcément un progrès.
Si tu ne peux pas produire une estimation défendable, fournis la méthode et les données manquantes au lieu d’un faux chiffre précis. Les facteurs moyens ne représentent pas nécessairement les émissions marginales d’un passager.

PASSER À L’ACTION
Recommande une première action facile à tester pendant une semaine. Explique comment noter le temps réel, le coût et la pénibilité ressentie. Signale les effets rebond possibles : trajets supplémentaires, détours importants ou hausse de la fréquence des déplacements. Ne généralise pas mon cas à tout le campus.`;
}
function regenerate(){output.value=makePrompt(Object.fromEntries(new FormData(form)));status.textContent='Prompt actualisé. Relisez-le, puis copiez-le dans l’IA de votre choix.';}
form.addEventListener('input',regenerate);form.addEventListener('change',regenerate);form.addEventListener('submit',event=>event.preventDefault());form.addEventListener('reset',()=>setTimeout(regenerate,0));
document.querySelector('#copy').addEventListener('click',async()=>{
 const success='Prompt complet copié. Ouvrez votre IA ci-dessous, puis collez-le dans une nouvelle conversation.';
 const manual='Le texte est sélectionné. Utilisez Copier sur votre appareil, puis collez-le dans votre IA.';
 output.focus({preventScroll:true});output.select();
 try{if(document.execCommand('copy')){status.textContent=success;return;}}catch{}
 status.textContent=manual;
 try{await Promise.race([navigator.clipboard.writeText(output.value),new Promise((_,reject)=>setTimeout(()=>reject(new Error('Clipboard timeout')),1200))]);status.textContent=success;}
 catch{status.textContent=manual;}
});
document.querySelector('#download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([output.value],{type:'text/plain;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download='mon-trajet-ibgbi-prompt.txt';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Le téléchargement du prompt au format texte est lancé.';});
regenerate();
