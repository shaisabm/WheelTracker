<script>
	let { size = 40 } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
	<!-- Outer circle (wheel) -->
	<circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="4" fill="none" class="text-blue-600"/>

	<!-- Inner circle -->
	<circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="3" fill="none" class="text-blue-500"/>

	<!-- Spokes -->
	<line x1="50" y1="5" x2="50" y2="25" stroke="currentColor" stroke-width="3" class="text-blue-600"/>
	<line x1="50" y1="75" x2="50" y2="95" stroke="currentColor" stroke-width="3" class="text-blue-600"/>
	<line x1="5" y1="50" x2="25" y2="50" stroke="currentColor" stroke-width="3" class="text-blue-600"/>
	<line x1="75" y1="50" x2="95" y2="50" stroke="currentColor" stroke-width="3" class="text-blue-600"/>

	<!-- Diagonal spokes -->
	<line x1="18" y1="18" x2="30" y2="30" stroke="currentColor" stroke-width="2.5" class="text-blue-500"/>
	<line x1="82" y1="18" x2="70" y2="30" stroke="currentColor" stroke-width="2.5" class="text-blue-500"/>
	<line x1="18" y1="82" x2="30" y2="70" stroke="currentColor" stroke-width="2.5" class="text-blue-500"/>
	<line x1="82" y1="82" x2="70" y2="70" stroke="currentColor" stroke-width="2.5" class="text-blue-500"/>

	<!-- Center hub -->
	<circle cx="50" cy="50" r="8" fill="currentColor" class="text-blue-600"/>

	<!-- Curved arrow indicating rotation (wheel strategy cycle) -->
	<path d="M 70 30 A 25 25 0 0 1 70 70" stroke="currentColor" stroke-width="3" fill="none"
	      stroke-linecap="round" class="text-green-500"/>
	<polygon points="73,68 70,75 65,70" fill="currentColor" class="text-green-500"/>
</svg>
