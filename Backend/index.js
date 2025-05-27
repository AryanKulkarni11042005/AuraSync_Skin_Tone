import Express from 'express';

const app = Express();
app.use(Express.json());
const PORT = 3000;


app.get('/', (req, res) => {
  res.send('Hello World!');
});


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
}); 