<!-- the boxes that are in the right column of the annotation editor and displays class definitions -->

<script>
    export let item = {
        title: "Placeholder title",
        text: "Placeholder text"
    };

    let title = item.title;
    let text = item.text;

</script>


<div class="border box bg-light rounded p-2 mt-1 text-small pb-0">
    <h6> <b>{title}</b> </h6>
    <p class="pb-0 mb-1"> <small>{text} </small> </p>
</div>


<style>

.box {
    cursor:default;
    margin-bottom: 10px;
}

</style>