<script>
	import { log } from '$lib/CustomLogger';
    import { Tooltip } from '@svelte-plugins/tooltips';
	import { onMount } from 'svelte';
	import { logout } from '../../routes/login/+page.svelte';
	import LoadingButton from './LoadingButton.svelte';


    onMount(() => {
        updateMethodSelection();
    });


    // Backend Method Selection Component
	let backendMethod = 'bilstm_crf';
    /**
	 * @type {string}
	 */
     export let token;

    function handleChange() {
		// create local storage entry for selected backend method
		log('admin', 'set selected backend method: ' + backendMethod);
		localStorage.setItem('backendMethod', backendMethod);
	}

    function updateMethodSelection() {
		// set the selected backend method to the one stored in local storage
		backendMethod = localStorage.getItem('backendMethod') ?? 'bilstm_crf';
	}

    function deleteAllLocalData() {
		localStorage.clear();
		//showSuccessMessage('Lokale Daten gelöscht');
		logout(token);
        return;
	}

</script>




<div>
    <div class="flex-item m-2 w-75">
        <h3>Modus</h3>
        <p class="infotext text-start w-100">
            Hier kann zwischen verschiedenen Methoden gewählt werden, mit denen die vorgeschlagenen Annotationen bestimmt werden. Rule-based ist sehr schnell. 
        XLM-R ist langsam, aber genau. BiLSTM-CRF ist ein Kompromiss aus Geschwindigkeit und Genauigkeit.</p>
                    <select
                        class="form-select m-2 model-choice-dropdown"
                        id="backendMethod"
                        bind:value={backendMethod}
                        on:change={handleChange}
                    >
                        <option value="rule-based">Rule-based</option>
                        <option value="bilstm_crf">BiLSTM-CRF</option>
                        <option value="xlm_r">XLM-R</option>
                    </select>
    </div>
    <div class="flex-item m-2">
        <h3>Cache</h3>
        <p class="infotext text-start w-75">
            Dies löscht alle lokal im Browser gespeicherten Daten, inklusive der aktuellen Session. Sie werden ausgeloggt.
            </p>
           

            <LoadingButton style="min-width: 210px;" buttonText="Cache löschen" onClick={() => deleteAllLocalData()}> </LoadingButton>

        
    </div>
</div>


<style>

    @import "../../global.css";


.model-choice-dropdown {
    width: 200px;
    display: inline-block;
}
    

.flex-item {
    display: flex;
    flex-direction: column;
    align-items: start;
    width: 100%;
}


 h3 {
    font-size: smaller;
    font-weight: bold;
    margin-bottom: 0.5em;
 }

 .infotext {
		font-weight: lighter;
        color: #616161;
		padding-left: 10px;
	}

</style>