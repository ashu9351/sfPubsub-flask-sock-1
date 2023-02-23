function callAPi(){
        
    const log = (text) => {
        text = JSON.parse(text);
        console.log(text.Name__c);
       
        var body = document.getElementById("tbody");
        body.innerHTML += '<tr><td><div class="slds-truncate" title="'+text.Fruit_Id__c+'">'+text.Fruit_Id__c+'</div></td>'+'<td><div class="slds-truncate" title="'+text.Name__c+'">'+text.Name__c+'</div></td>'+
                                    '<td><div class="slds-truncate" title="'+text.Price__c+'">'+text.Price__c+'</div></td>'+'<td><div class="slds-truncate" title="'+text.is_Subsidised__c+'">'+text.is_Subsidised__c+'</div></td></tr>';
       
       
    };
    
    const socket = new WebSocket('ws://' + location.host + '/echo');
    socket.onopen = function(e) {
        alert("[open] Connection established");
        console.log("Sending to server");
       
        //socket.send('Hello');
        socket.addEventListener('message', ev => {
        log(ev.data);
        });
    };
   
}
window.onload = callAPi();