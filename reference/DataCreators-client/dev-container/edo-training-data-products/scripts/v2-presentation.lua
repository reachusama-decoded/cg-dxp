-- Render original learner emoji as small textual indicators in print.
-- Source Markdown and full block-coverage hashes remain unchanged.
local substitutions = {
 ['🚀']='[advanced]', ['🎯']='[goal]', ['🧠']='[concept]', ['🔍']='[inspect]',
 ['🛠️']='[tools]', ['🛠']='[tools]', ['📚']='[reference]', ['🧪']='[check]',
 ['🏁']='[finish]', ['⚠️']='[note]', ['⚠']='[note]', ['💡']='[hint]',
 ['✅']='[pass]', ['❌']='[fail]', ['☑']='[x]', ['▸']='>',
 ['📌']='[note]', ['📊']='[data]', ['👉']='[next]', ['📝']='[write]',
 ['⏱️']='[time]', ['⏱']='[time]', ['🔗']='[link]', ['👥']='[team]'
}
function Str(el)
 for from,to in pairs(substitutions) do el.text=el.text:gsub(from,to) end
 return el
end
