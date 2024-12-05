<script>
    import { onMount } from 'svelte';
  
    export let top = '2em';
    export let left = '2em';
    export let tips = [];
    export let pageId; // Unique identifier for each page
    let minimized = false;
    let tipboxClosed = false;
  
    function toggleMinimize() {
      minimized = !minimized;
    }
  
    function closeTipBox() {
      tipboxClosed = true;
      sessionStorage.setItem(`tipboxClosed_${pageId}`, 'true');
    }
  
    function expandTipBox() {
      minimized = false;
    }
  
    onMount(() => {
      if (sessionStorage.getItem(`tipboxClosed_${pageId}`) === 'true') {
        tipboxClosed = true;
      }
    });
  </script>
  
  {#if !tipboxClosed}
    <div class="tipbox" style="top: {top}; left: {left};">
      <div class="tipboxheader" style="{minimized ? 'border-radius: 15px;' : ''}">
        <h2 style="margin-right: 3em;">💡 Tipps und Tricks </h2>
        <div style="float: right;">
          {#if minimized}
            <button class="tipboxbutton" on:click={expandTipBox}></button>
          {/if}
          <button class="tipboxbutton" on:click={toggleMinimize}>
            {#if minimized}
              +
            {:else}
              -
            {/if}
          </button>
          <button class="tipboxbutton" on:click={closeTipBox}>&times;</button>
        </div>
      </div>
      {#if !minimized}
        <div class="tipboxbody">
          <ul class="tipbox-bulletpoint-list">
            {#each tips as tip}
              <li><b>{tip.title}</b>: {tip.description}</li>
            {/each}
          </ul>
        </div>
      {/if}
    </div>
  {/if}
  
  <style>

    .tipbox-bulletpoint-list {
      margin: 0.5em; list-style-type: none;
    }

    .tipbox {
      position: absolute;
      transform: translate(-50%, -50%);
      border: 1px solid #ccc;
      border-radius: 15px;
      background-color: #f9f9f9;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      z-index: 1000;
    }
  
    .tipboxheader {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background-color: #9999ff;
      border-radius: 15px 15px 0 0;
      color: rgb(19, 18, 18);
      padding: 5px;
      padding-left: 2em;
      padding-right: 2em;
    }
  
    .tipboxheader h2 {
      margin: 0;
      font-size: 20px;
      color: white;
    }
  
    .tipboxbody {
      padding: 10px;
    }
  
    .tipboxbutton {
      background-color: transparent;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 20px;
    }
  </style>
  