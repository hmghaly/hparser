from itertools import groupby

sent="I saw the boy with the telescope"
#sent="they discussed the mistakes in the second meeting"
sent_tokens=sent.split()
pos_dict={}
pos_dict["i"]={"PRP":1}
pos_dict["they"]={"PRP":1}
pos_dict["saw"]={"VBD":1}
pos_dict["discussed"]={"VBD":1}
pos_dict["the"]={"DT":1}
pos_dict["boy"]={"NN":1}
pos_dict["with"]={"IN":1}
pos_dict["in"]={"IN":1}
pos_dict["telescope"]={"NN":1}
pos_dict["meeting"]={"NN":1}
pos_dict["mistakes"]={"NNS":1}
pos_dict["second"]={"JJ":1}


rules_dict={}
rules_dict["PRP"]={"":"NP"}
rules_dict["NN"]={"":"NP"}
rules_dict["NNS"]={"":"NP"}
rules_dict["VBD"]={"":"V"}
rules_dict["NP"]={"V":"VP","NN":"NP","IN":"PP","DT":"NP","JJ":"NP"}
rules_dict["PP"]={"VP":"VP","NP":"NP"}
rules_dict["VP"]={"NP":"S"}


def get_structure(node,node_list,level):
    node_span,node_wt=tag_dict[node]
    node_children=merge_dict.get(node,[])
    node_list.append((node, node_span,node_wt, level))
    for ch_node in node_children:
        node_list=get_structure(ch_node,node_list,level+1)
    return node_list
    
    
    
    

def check_previous(cur_tag_id,span_dict,end_dict,tag_counter,tag_dict,merge_dict,depth):
    if depth>10: return span_dict,end_dict,tag_counter,tag_dict, merge_dict
    cur_tag_name=cur_tag_id.split("_")[0]
    print "cur_tag_name", cur_tag_name
    cur_tag_span,cur_tag_wt=tag_dict[cur_tag_id]
    local_rule_dict=rules_dict.get(cur_tag_name,{})
    prev_phrases=[]
    cur_i=cur_tag_span[0]
    if cur_i>0:
        prev_phrases_tags=end_dict[cur_i-1]
        for prev_tag_id in prev_phrases_tags:
            prev_tag_name=prev_tag_id.split("_")[0]
            prev_tag_span,prev_tag_wt=tag_dict[prev_tag_id]
            combined_tag_name=local_rule_dict.get(prev_tag_name)
            if combined_tag_name==None: continue
            combined_tag_wt=cur_tag_wt+prev_tag_wt
            combined_tag_span=(prev_tag_span[0],cur_tag_span[1])
            combined_tag_count=tag_counter.get(combined_tag_name,0)
            combined_tag_id="%s_%s"%(combined_tag_name,combined_tag_count)
            tag_counter[combined_tag_name]=combined_tag_count+1
            tag_dict[combined_tag_id]=(combined_tag_span,combined_tag_wt)
            #print "combined_tag_id", combined_tag_id, "prev", prev_tag_id, "current", cur_tag_id, "span", combined_tag_span
            
            temp=span_dict.get(combined_tag_span,[])
            temp.append(combined_tag_id)
            span_dict[combined_tag_span]=temp

            temp_end=end_dict.get(combined_tag_span[1],[])
            temp_end.append(combined_tag_id)
            end_dict[combined_tag_span[1]]=temp_end

            merge_dict[combined_tag_id]=[prev_tag_id,cur_tag_id]
            span_dict,end_dict,tag_counter,tag_dict, merge_dict=check_previous(combined_tag_id,span_dict,end_dict,tag_counter,tag_dict,merge_dict,depth+1)

    return span_dict,end_dict,tag_counter,tag_dict, merge_dict
    



print sent_tokens
print pos_dict

span_dict={}
end_dict={}
tag_counter={}
tag_dict={}
merge_dict={}

for i, t in enumerate(sent_tokens):
    cur_tags=pos_dict[t.lower()]
    for tag in cur_tags:
        tag_wt=cur_tags[tag]
        #print i, t, tag, tag_wt
        tag_count=tag_counter.get(tag,0)
        tag_id="%s_%s"%(tag,tag_count)
        tag_counter[tag]=tag_count+1
        tag_dict[tag_id]=((i,i),tag_wt)
        
        temp=span_dict.get((i,i),[])
        temp.append(tag_id)
        span_dict[(i,i)]=temp

        temp_end=end_dict.get(i,[])
        temp_end.append(tag_id)
        end_dict[i]=temp_end

        cur_rules=rules_dict.get(tag,{})

        
        for cr in cur_rules:
            if cr=="":
                new_tag=cur_rules[cr]
                new_tag_count=tag_counter.get(new_tag,0)
                new_tag_id="%s_%s"%(new_tag,new_tag_count)
                tag_counter[new_tag]=new_tag_count+1
                tag_dict[new_tag_id]=((i,i),tag_wt)
                
                temp=span_dict.get((i,i),[])
                temp.append(new_tag_id)
                span_dict[(i,i)]=temp

                temp_end=end_dict.get(i,[])
                temp_end.append(new_tag_id)
                end_dict[i]=temp_end
                merge_dict[new_tag_id]=[tag_id]
                span_dict,end_dict,tag_counter,tag_dict, merge_dict=check_previous(new_tag_id,span_dict,end_dict,tag_counter,tag_dict,merge_dict,1)
            else:
                span_dict,end_dict,tag_counter,tag_dict, merge_dict=check_previous(tag_id,span_dict,end_dict,tag_counter,tag_dict,merge_dict,1)
                
                

html="<html><body>"
full_spans=span_dict[(0,len(sent_tokens)-1)]
for f in full_spans:
    html+='<table border="1">'
    cur_node_list=get_structure(f,[],0)
    cur_node_list.sort(key=lambda x:(x[-1],x[1]))
    grouped=[list(group) for key,group in groupby(cur_node_list,lambda x:x[-1])]
    for grp in grouped:
        html+="<tr>"
        print grp
        span_tag_dict={}
        all_xs=[0]
        for g0 in grp:
            s0,s1=g0[1]
            span_tag_dict[(s0,s1+1)]=g0[0]
            all_xs.append(s0)
            all_xs.append(s1+1)
            print g0
        all_xs.append(len(sent_tokens))
        all_xs=sorted(list(set(all_xs)))
        print all_xs
        print span_tag_dict
        for z0,z1 in zip(all_xs,all_xs[1:]):
            cur_colspan=z1-z0
            cur_tag=span_tag_dict.get((z0,z1),"")
            print z0, z1, cur_colspan, cur_tag
            cur_td='<td colspan="%s" align="center">%s</td>'%(cur_colspan,cur_tag)
            html+=cur_td
            
 
        html+="</tr>"
        
    print '------'
    html+="<tr>"
    for t in sent_tokens:
        cur_td='<td colspan="%s" align="center">%s</td>'%(1,t)
        html+=cur_td
    html+="</tr>"
        
    html+='</table><br><br>'

html+="</body></html>"

fopen=open("parse_out.html","w")
fopen.write(html)
fopen.close()

##    print f
##    print tag_dict[f]
##    print merge_dict[f]
##    print '-------'


